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

func initDiscord(token, statsFolder, apiURL string) (*discordgo.Session, error) {
	dg, err := discordgo.New("Bot " + token)
	if err != nil {
		return nil, err
	}

	dg.Identify.Intents =
		discordgo.IntentsGuilds |
			discordgo.IntentsGuildMessages |
			discordgo.IntentsMessageContent

	registeredCommands := commands.New(statsFolder, apiURL)
	dg.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		if i.Type != discordgo.InteractionApplicationCommand {
			return
		}
		cmdName := i.ApplicationCommandData().Name
		cmd, ok := registeredCommands[cmdName]
		if !ok {
			return
		}
		cmd.Handler(s, i)
	})

	if err := dg.Open(); err != nil {
		return nil, err
	}

	for name, cmd := range registeredCommands {
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
		return nil, err
	}

	return rcon, nil
}

// StatusWatcher continua igual, monitorando snapshot e status do servidor
func startServerStatusWatcher(dg *discordgo.Session, statusChannelID, statusMessageID, serverAddr, domain string) error {
	monitor := &server.ServerMonitor{
		ServerAddr: serverAddr,
		Interval:   2 * time.Second,
		StatusEmbed: &server.StatusEmbed{
			Session:   dg,
			ChannelID: statusChannelID,
			MessageID: statusMessageID,
			BotName:   dg.State.User.Username,
			Domain:    domain,
		},
		// PlayerEvents via snapshot pode ser removido ou mantido como fallback
	}
	monitor.Start()
	return nil
}

func startMCWatcher(dg *discordgo.Session, eventsChannelID, logPath, apiURL string, rcon *connections.Chat) error {
	mcBridge, err := presentation.NewMinecraftChatBridge(dg, eventsChannelID)
	if err != nil {
		return err
	}

	playerTracker := presentation.NewPlayerTracking(dg, eventsChannelID)

	players, err := rcon.ListPlayers()
	if err != nil {
		log.LogError("erro ao obter players via RCON:", err)
	} else {
		playerTracker.SyncInitial(players)
	}

	watcher := log.New(logPath)
	watcher.Register(func(line string) {
		mcBridge.Handle(line)
	})
	watcher.Register(func(line string) {
		presentation.ProcessAdvancementLine(dg, eventsChannelID, line)
	})
	watcher.Register(func(line string) {
		presentation.ProcessDeathLine(dg, eventsChannelID, line, apiURL)
	})
	watcher.Register(func(line string) {
		presentation.ProcessMobDeath(line, dg, eventsChannelID, apiURL)
	})
	watcher.Register(func(line string) {
		playerTracker.HandleLogLine(line)
	})

	go watcher.Start()
	return nil
}
