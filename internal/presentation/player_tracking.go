package presentation

import (
	"fmt"
	"strings"

	"discord-bot-go/internal/connections"

	"github.com/bwmarrin/discordgo"
)

type PlayerTracking struct {
	Session   *discordgo.Session
	ChannelID string
	players   map[string]struct{}
}

func NewPlayerTracking(session *discordgo.Session, channelID string) *PlayerTracking {
	return &PlayerTracking{
		Session:   session,
		ChannelID: channelID,
		players:   make(map[string]struct{}),
	}
}

func (p *PlayerTracking) HandleLogLine(line string) {
	line = strings.TrimSpace(line)
	if line == "" {
		return
	}

	var player string
	var joined bool

	switch {
	case strings.Contains(line, "joined the game"):
		player = extractPlayerName(line)
		joined = true
	case strings.Contains(line, "lost connection"), strings.Contains(line, "left the game"):
		player = extractPlayerName(line)
		joined = false
	default:
		return
	}

	if player == "Anonymous Player" {
		return
	}

	if joined {
		if _, exists := p.players[player]; !exists {
			p.players[player] = struct{}{}
			p.sendEvent(player, true)
		}
	} else {
		if _, exists := p.players[player]; exists {
			delete(p.players, player)
			p.sendEvent(player, false)
		}
	}
}

func extractPlayerName(line string) string {
	parts := strings.Split(line, " ")
	if len(parts) > 0 {
		for i, part := range parts {
			if part == "joined" || part == "left" || part == "lost" {
				if i > 0 {
					return strings.Trim(parts[i-1], "[]")
				}
			}
		}
	}
	return "Unknown"
}

func (p *PlayerTracking) sendEvent(player string, joined bool) {
	color := 0xFF0000
	text := "saiu do servidor"
	if joined {
		color = 0x00FF00
		text = "entrou no servidor"
	}

	reader, filename, err := connections.GetPlayerImage(player)
	var iconURL string
	var files []*discordgo.File

	if err != nil || reader == nil {
		iconURL = fmt.Sprintf("https://mineskin.eu/helm/%s", player)
	} else {
		iconURL = "attachment://" + filename
		files = []*discordgo.File{
			{
				Name:   filename,
				Reader: reader,
			},
		}
	}

	embed := &discordgo.MessageEmbed{
		Color: color,
		Author: &discordgo.MessageEmbedAuthor{
			Name:    fmt.Sprintf("%s %s", player, text),
			IconURL: iconURL,
		},
	}

	_, err = p.Session.ChannelMessageSendComplex(p.ChannelID, &discordgo.MessageSend{
		Embed: embed,
		Files: files,
	})
	if err != nil {
		fmt.Printf("[ERROR] Falha ao enviar embed do jogador %s: %v\n", player, err)
	}
}
