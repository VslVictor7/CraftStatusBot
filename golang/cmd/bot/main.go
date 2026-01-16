package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"discord-bot-go/internal/commands"
	"discord-bot-go/internal/server"

	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
)

func main() {

	godotenv.Load()

	token := os.Getenv("DISCORD_TOKEN")
	channel_id := os.Getenv("CHANNEL_ID")
	message_id := os.Getenv("MESSAGE_ID")
	events_channel_id := os.Getenv("EVENTS_CHANNEL_ID")

	dg, err := discordgo.New("Bot " + token)
	if err != nil {
		fmt.Println("Erro ao criar sessão:", err)
		return
	}

	dg.Identify.Intents = discordgo.IntentsGuilds

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
		fmt.Println("registrando comandos")
		_, err := dg.ApplicationCommandCreate(
			dg.State.User.ID,
			"",
			cmd.Command(),
		)
		if err != nil {
			fmt.Printf("Erro ao registrar /%s: %v\n", name, err)
		}
	}

	monitor := &server.ServerMonitor{
		ServerAddr: "localhost:25565",
		Interval:   2 * time.Second,

		StatusEmbed: &server.StatusEmbed{
			Session:   dg,
			ChannelID: channel_id,
			MessageID: message_id,
			BotName:   dg.State.User.Username,
		},

		PlayerEvents: &server.PlayerEvents{
			Session:   dg,
			ChannelID: events_channel_id,
		},
	}

	monitor.Start()

	fmt.Println("bot ta rodando")

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	<-stop

	fmt.Println("desligando")
	_ = dg.Close()
}
