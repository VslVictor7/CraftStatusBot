package server

import (
	"fmt"

	"github.com/bwmarrin/discordgo"
)

type PlayerEvents struct {
	Session   *discordgo.Session
	ChannelID string

	lastPlayers []string
	initialized bool
}

func (p *PlayerEvents) Update(snapshot *ServerSnapshot) {
	if !p.initialized {
		p.lastPlayers = snapshot.PlayerNames
		p.initialized = true
		return
	}

	joined := difference(snapshot.PlayerNames, p.lastPlayers)
	left := difference(p.lastPlayers, snapshot.PlayerNames)

	for _, name := range joined {
		p.sendEvent(name, true)
	}

	for _, name := range left {
		p.sendEvent(name, false)
	}

	p.lastPlayers = snapshot.PlayerNames
}

func (p *PlayerEvents) sendEvent(player string, joined bool) {
	var (
		color int
		text  string
	)

	if joined {
		color = 0x00FF00
		text = "entrou no servidor"
	} else {
		color = 0xFF0000
		text = "saiu do servidor"
	}

	embed := &discordgo.MessageEmbed{
		Color: color,
		Author: &discordgo.MessageEmbedAuthor{
			Name: fmt.Sprintf("%s %s", player, text),
			IconURL: fmt.Sprintf(
				"https://mineskin.eu/helm/%s",
				player, // username funciona como fallback
			),
		},
	}

	_, err := p.Session.ChannelMessageSendEmbed(p.ChannelID, embed)
	if err != nil {
		fmt.Printf("[ERROR] Erro ao enviar webhook de evento de jogador %s: %v\n", player, err)
		return
	}
}

func difference(a, b []string) []string {
	var diff []string
	for _, x := range a {
		if !contains(b, x) {
			diff = append(diff, x)
		}
	}
	return diff
}
