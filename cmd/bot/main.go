package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"discord-bot-go/internal/commands"
	"discord-bot-go/internal/connections"
	"discord-bot-go/internal/presentation"
	"discord-bot-go/internal/server"

	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
)

func main() {
	godotenv.Load()

	token := os.Getenv("DISCORD_TOKEN")

	serverAddr := os.Getenv("HOST")

	statusChannelID := os.Getenv("CHANNEL_ID")
	statusMessageID := os.Getenv("MESSAGE_ID")

	eventsChannelID := os.Getenv("EVENTS_CHANNEL_ID")

	rconAddr := os.Getenv("RCON_ADDR")
	rconPassword := os.Getenv("RCON_PASSWORD")

	dg, err := discordgo.New("Bot " + token)
	if err != nil {
		fmt.Println("Erro ao criar sessão:", err)
		return
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
		fmt.Println("Erro ao abrir conexão:", err)
		return
	}

	for name, cmd := range commands.RegisteredCommands {
		_, err := dg.ApplicationCommandCreate(
			dg.State.User.ID,
			"",
			cmd.Command(),
		)
		if err != nil {
			fmt.Printf("Erro ao registrar /%s: %v\n", name, err)
		}
	}

	rconChat := &connections.Chat{
		Addr:     rconAddr,
		Password: rconPassword,
	}

	if err := rconChat.Connect(); err != nil {
		fmt.Println("Erro ao conectar no RCON:", err)
		return
	}
	defer rconChat.Close()

	chatBridge := &presentation.DiscordChatBridge{
		Session:   dg,
		ChannelID: eventsChannelID,
		RconChat:  rconChat,
	}
	chatBridge.Register()

	monitor := &server.ServerMonitor{
		ServerAddr: serverAddr,
		Interval:   2 * time.Second,

		StatusEmbed: &server.StatusEmbed{
			Session:   dg,
			ChannelID: statusChannelID,
			MessageID: statusMessageID,
			BotName:   dg.State.User.Username,
		},

		PlayerEvents: &server.PlayerEvents{
			Session:   dg,
			ChannelID: eventsChannelID,
		},
	}

	monitor.Start()

	fmt.Println("Bot rodando")

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	<-stop

	fmt.Println("Desligando bot")
	_ = dg.Close()
}
