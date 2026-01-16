package main

import (
	"discord-bot-go/internal/presentation"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/joho/godotenv"
)

func main() {
	godotenv.Load()

	token := os.Getenv("DISCORD_TOKEN")
	rconAddr := os.Getenv("RCON_ADDR")
	rconPassword := os.Getenv("RCON_PASSWORD")
	statusChannelID := os.Getenv("CHANNEL_ID")
	statusMessageID := os.Getenv("MESSAGE_ID")
	serverAddr := os.Getenv("HOST")
	eventsChannelID := os.Getenv("EVENTS_CHANNEL_ID")
	logPath := os.Getenv("SERVER_LOG_PATH")

	dg, err := initDiscord(token)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer dg.Close()

	rcon, err := initRcon(rconAddr, rconPassword)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer rcon.Close()

	chatBridge := &presentation.DiscordChatBridge{
		Session:   dg,
		ChannelID: eventsChannelID,
		RconChat:  rcon,
	}
	chatBridge.Register()

	if err := startServerStatusWatcher(dg, eventsChannelID, statusChannelID, statusMessageID, serverAddr); err != nil {
		fmt.Println(err)
		return
	}

	if err := startMCWatcher(dg, eventsChannelID, logPath); err != nil {
		fmt.Println(err)
		return
	}

	fmt.Println("Bot rodando")

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	<-stop

	fmt.Println("Desligando bot")
}
