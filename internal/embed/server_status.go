package embed

import (
	"fmt"
	"strings"
	"time"

	"os"

	"github.com/bwmarrin/discordgo"
)

func BuildServerEmbed(
	online bool,
	players int,
	version string,
	names []string,
	botName string,
) *discordgo.MessageEmbed {

	domain := os.Getenv("DOMAIN")

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

	filteredNames := []string{}
	for _, n := range names {
		if n != "Anonymous Player" {
			filteredNames = append(filteredNames, n)
		}
	}

	namesValue := "Nenhum"
	if len(filteredNames) > 0 {
		namesValue = strings.Join(filteredNames, ", ")
	}

	return &discordgo.MessageEmbed{
		Title: "Status do Servidor Minecraft",
		Color: color,
		Fields: []*discordgo.MessageEmbedField{
			{
				Name:  "🖥️ IP",
				Value: domain,
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
