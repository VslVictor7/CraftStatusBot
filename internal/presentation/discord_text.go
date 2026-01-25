package presentation

import (
	"encoding/json"
	"strings"

	"discord-bot-go/internal/connections"
	"discord-bot-go/internal/log"

	"github.com/bwmarrin/discordgo"
)

type DiscordChatBridge struct {
	Session    *discordgo.Session
	ChannelID  string
	RconChat   *connections.Chat
	MessageFmt string
}

func (d *DiscordChatBridge) Register() {
	d.Session.AddHandler(d.onMessage)
}

func (d *DiscordChatBridge) onMessage(
	s *discordgo.Session,
	m *discordgo.MessageCreate,
) {
	if m.Author.Bot {
		return
	}

	if m.ChannelID != d.ChannelID {
		return
	}

	content := strings.TrimSpace(m.Content)
	if content == "" {
		return
	}

	payload := []map[string]any{
		{
			"text":  "[Discord] ",
			"color": "aqua",
		},
		{
			"text":  m.Author.Username + " ",
			"color": "white",
			"bold":  false,
		},
		{
			"text":  "» ",
			"color": "white",
			"bold":  false,
		},
		{
			"text":  content,
			"color": "white",
			"bold":  false,
		},
	}

	b, err := json.Marshal(payload)
	if err != nil {
		log.LogError("erro ao montar tellraw:", err)
		return
	}

	if err := d.RconChat.Tellraw(string(b)); err != nil {
		log.LogError("erro ao enviar tellraw:", err)
		return
	}
}
