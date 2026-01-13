package main

import (
	"discord-bot-go/internal/commands"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
)

func main() {
	godotenv.Load()

	token := os.Getenv("DISCORD_TOKEN")
	if token == "" {
		fmt.Println("DISCORD_TOKEN não definido")
		return
	}

	dg, err := discordgo.New("Bot " + token)
	if err != nil {
		fmt.Println("Erro ao criar sessão:", err)
		return
	}

	dg.Identify.Intents = discordgo.IntentsGuilds

	dg.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		commands.PingHandler(s, i)
	})

	err = dg.Open()
	if err != nil {
		fmt.Println("Erro ao abrir conexão:", err)
		return
	}

	// Registro do comando
	_, err = dg.ApplicationCommandCreate(
		dg.State.User.ID,
		"",
		commands.PingCommand,
	)
	if err != nil {
		fmt.Println("Erro ao registrar /ping:", err)
	}

	fmt.Println("bot rodando")

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	<-stop

	dg.Close()
}
