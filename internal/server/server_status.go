package server

import (
	"discord-bot-go/internal/log"
	"fmt"
	"strings"
	"time"

	"github.com/bwmarrin/discordgo"
)

type StatusEmbed struct {
	Session   *discordgo.Session
	ChannelID string
	MessageID string
	BotName   string
	Domain    string

	lastState *ServerSnapshot
}

func (s *StatusEmbed) Update(snapshot *ServerSnapshot) {
	if snapshot == nil {
		return
	}

	if s.lastState != nil && snapshotsEqual(s.lastState, snapshot) {
		return
	}

	embed := BuildServerEmbed(
		snapshot.Online,
		snapshot.PlayerCount,
		snapshot.Version,
		snapshot.PlayerNames,
		s.BotName,
		s.Domain,
	)

	_, err := s.Session.ChannelMessageEditEmbed(
		s.ChannelID,
		s.MessageID,
		embed,
	)
	if err != nil {
		log.LogError("Erro ao atualizar embed de status do servidor:", err)
		return
	}

	s.lastState = snapshot
}

func snapshotsEqual(a, b *ServerSnapshot) bool {
	if a.Online != b.Online {
		return false
	}
	if a.PlayerCount != b.PlayerCount {
		return false
	}
	if a.Version != b.Version {
		return false
	}
	if len(a.PlayerNames) != len(b.PlayerNames) {
		return false
	}
	for i := range a.PlayerNames {
		if a.PlayerNames[i] != b.PlayerNames[i] {
			return false
		}
	}
	return true
}

func BuildServerEmbed(
	online bool,
	players int,
	version string,
	names []string,
	botName, domain string,
) *discordgo.MessageEmbed {

	color := 0xff0000
	status := "🔴 Offline"
	if online {
		color = 0x00ff00
		status = "🟢 Online"
	} else {
		version = "N/A"
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
