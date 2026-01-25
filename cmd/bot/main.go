package main

import (
	"discord-bot-go/internal/presentation"
	"os"
	"os/signal"
	"syscall"

	"discord-bot-go/internal/log"

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
		log.LogError("Falha ao iniciar o bot", err)
		return
	}
	defer dg.Close()

	log.LogInfo("Conectado ao Discord")

	rcon, err := initRcon(rconAddr, rconPassword)
	if err != nil {
		log.LogError("Falha ao iniciar RCON", err)
		return
	}
	defer rcon.Close()

	chatBridge := &presentation.DiscordChatBridge{
		Session:   dg,
		ChannelID: eventsChannelID,
		RconChat:  rcon,
	}
	chatBridge.Register()

	log.LogInfo("Bridge RCON conectado ao servidor Minecraft e Discord")

	if err := startServerStatusWatcher(dg, eventsChannelID, statusChannelID, statusMessageID, serverAddr); err != nil {
		log.LogError("Falha ao iniciar o monitor de status do servidor", err)
		return
	}

	log.LogInfo("Status do servidor sendo monitorado")
	if err := startMCWatcher(dg, eventsChannelID, logPath); err != nil {
		log.LogError("Falha ao iniciar o watcher de logs do Minecraft", err)
		return
	}

	log.LogInfo("Watcher de logs do Minecraft iniciado")
	log.LogOk("Bot iniciado com sucesso")

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	<-stop

	log.LogInfo("Bot Desligando bot...")
}
