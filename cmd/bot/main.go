package main

import (
	"discord-bot-go/internal/config"
	"discord-bot-go/internal/presentation"
	"os"
	"os/signal"
	"syscall"

	"discord-bot-go/internal/log"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.LogError("Configuração inválida", err)
		return
	}

	dg, err := initDiscord(cfg.DiscordToken, cfg.StatsFolder, cfg.APIURL)
	if err != nil {
		log.LogError("Falha ao iniciar o bot", err)
		return
	}
	defer dg.Close()

	log.LogInfo("Conectado ao Discord")

	rcon, err := initRcon(cfg.RCONAddr, cfg.RCONPassword)
	if err != nil {
		log.LogError("Falha ao iniciar RCON", err)
		return
	}
	defer rcon.Close()

	chatBridge := &presentation.DiscordChatBridge{
		Session:   dg,
		ChannelID: cfg.EventsChannelID,
		RconChat:  rcon,
	}
	chatBridge.Register()

	log.LogInfo("Bridge RCON conectado ao servidor Minecraft e Discord")

	if err := startServerStatusWatcher(dg, cfg.StatusChannelID, cfg.StatusMessageID, cfg.ServerAddr, cfg.Domain); err != nil {
		log.LogError("Falha ao iniciar o monitor de status do servidor", err)
		return
	}

	log.LogInfo("Status do servidor sendo monitorado")
	if err := startMCWatcher(dg, cfg.EventsChannelID, cfg.LogPath, cfg.APIURL, rcon); err != nil {
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
