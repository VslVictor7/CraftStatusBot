package server

import (
	"fmt"

	"discord-bot-go/internal/embed"

	"github.com/bwmarrin/discordgo"
)

type StatusEmbed struct {
	Session   *discordgo.Session
	ChannelID string
	MessageID string
	BotName   string

	lastState *ServerSnapshot
}

func (s *StatusEmbed) Update(snapshot *ServerSnapshot) {
	if snapshot == nil {
		return
	}

	if s.lastState != nil && snapshotsEqual(s.lastState, snapshot) {
		return
	}

	embed := embed.BuildServerEmbed(
		snapshot.Online,
		snapshot.PlayerCount,
		snapshot.Version,
		snapshot.PlayerNames,
		s.BotName,
	)

	_, err := s.Session.ChannelMessageEditEmbed(
		s.ChannelID,
		s.MessageID,
		embed,
	)
	if err != nil {
		fmt.Println("erro ao atualizar embed:", err)
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
