package main

import (
	"fmt"
	"time"

	"discord-bot-go/internal/commands"
	"discord-bot-go/internal/connections"
	"discord-bot-go/internal/log"
	"discord-bot-go/internal/presentation"
	"discord-bot-go/internal/server"

	"github.com/bwmarrin/discordgo"
)

func initDiscord(token string) (*discordgo.Session, error) {
	dg, err := discordgo.New("Bot " + token)
	if err != nil {
		return nil, fmt.Errorf("erro ao criar sessão Discord: %w", err)
	}

	dg.Identify.Intents =
		discordgo.IntentsGuilds |
			discordgo.IntentsGuildMessages |
			discordgo.IntentsMessageContent

	dg.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		if i.Type != discordgo.InteractionApplicationCommand {
			return
		}
		cmdName := i.ApplicationCommandData().Name
		cmd, ok := commands.RegisteredCommands[cmdName]
		if !ok {
			return
		}
		cmd.Handler(s, i)
	})

	if err := dg.Open(); err != nil {
		return nil, fmt.Errorf("erro ao abrir conexão Discord: %w", err)
	}

	for name, cmd := range commands.RegisteredCommands {
		_, err := dg.ApplicationCommandCreate(dg.State.User.ID, "", cmd.Command())
		if err != nil {
			fmt.Printf("Erro ao registrar /%s: %v\n", name, err)
		}
	}

	return dg, nil
}

func initRcon(addr, password string) (*connections.Chat, error) {
	rcon := &connections.Chat{
		Addr:     addr,
		Password: password,
	}

	if err := rcon.Connect(); err != nil {
		return nil, fmt.Errorf("[ERROR] Erro ao conectar no RCON: %w | Desligando...", err)
	}

	return rcon, nil
}

// StatusWatcher continua igual, monitorando snapshot e status do servidor
func startServerStatusWatcher(dg *discordgo.Session, eventsChannelID, statusChannelID, statusMessageID, serverAddr string) error {
	monitor := &server.ServerMonitor{
		ServerAddr: serverAddr,
		Interval:   2 * time.Second,
		StatusEmbed: &server.StatusEmbed{
			Session:   dg,
			ChannelID: statusChannelID,
			MessageID: statusMessageID,
			BotName:   dg.State.User.Username,
		},
		// PlayerEvents via snapshot pode ser removido ou mantido como fallback
	}
	monitor.Start()
	return nil
}

func startMCWatcher(dg *discordgo.Session, eventsChannelID, logPath string) error {
	mcBridge, err := presentation.NewMinecraftChatBridge(dg, eventsChannelID)
	if err != nil {
		return fmt.Errorf("erro ao criar bridge MC: %w", err)
	}

	playerTracker := presentation.NewPlayerTracking(dg, eventsChannelID)

	watcher := log.New(logPath)
	watcher.Register(func(line string) {
		mcBridge.Handle(line)
	})
	watcher.Register(func(line string) {
		presentation.ProcessAdvancementLine(dg, eventsChannelID, line)
	})
	watcher.Register(func(line string) {
		presentation.ProcessDeathLine(dg, eventsChannelID, line)
	})
	watcher.Register(func(line string) {
		presentation.ProcessMobDeath(line, dg, eventsChannelID)
	})
	watcher.Register(func(line string) {
		playerTracker.HandleLogLine(line)
	})

	go watcher.Start()
	return nil
}
