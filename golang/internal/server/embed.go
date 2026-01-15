package server

import (
	"fmt"
	"strings"
	"time"

	"os"

	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
)

func BuildServerEmbed(
	online bool,
	players int,
	version string,
	names []string,
	botName string,
) *discordgo.MessageEmbed {

	godotenv.Load()

	host := os.Getenv("HOST")

	color := 0xff0000
	status := "🔴 Offline"
	if online {
		color = 0x00ff00
		status = "🟢 Online"
	}

	playerCountText := "Nenhum"

	if players > 0 {
		suffix := "jogadores"
		if players == 1 {
			suffix = "jogador"
		}
		playerCountText = fmt.Sprintf("%d %s", players, suffix)
	}

	namesValue := "Nenhum"
	if len(names) > 0 {
		namesValue = strings.Join(names, ", ")
	}

	return &discordgo.MessageEmbed{
		Title: "Status do Servidor Minecraft",
		Color: color,
		Fields: []*discordgo.MessageEmbedField{
			{
				Name:  "🖥️ IP",
				Value: host,
			},
			{
				Name:  "📶 Status",
				Value: status,
			},
			{
				Name:  "👥 Jogadores Online",
				Value: playerCountText,
			},
			{
				Name:  "📝 Nomes",
				Value: namesValue,
			},
			{
				Name:  "🌐 Versão",
				Value: version,
			},
		},
		Footer: &discordgo.MessageEmbedFooter{
			Text: botName,
		},
		Timestamp: time.Now().Format(time.RFC3339),
	}
}
