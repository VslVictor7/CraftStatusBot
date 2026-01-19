package presentation

import (
	"fmt"
	stdlog "log"
	"strings"

	"discord-bot-go/internal/connections"

	"github.com/bwmarrin/discordgo"
)

type MinecraftChatBridge struct {
	Session   *discordgo.Session
	ChannelID string

	Webhook *discordgo.Webhook
}

type ChatMessage struct {
	Player  string
	Message string
}

func NewMinecraftChatBridge(
	s *discordgo.Session,
	channelID string,
) (*MinecraftChatBridge, error) {

	wh, err := connections.EnsureWebhook(
		s,
		channelID,
		"Minecraft Chat Webhook",
	)
	if err != nil {
		return nil, err
	}

	return &MinecraftChatBridge{
		Session:   s,
		ChannelID: channelID,
		Webhook:   wh,
	}, nil
}

func (b *MinecraftChatBridge) Handle(line string) {
	msg, ok := ParseChatLine(line)
	if !ok {
		return
	}

	avatarURL := fmt.Sprintf(
		"https://mineskin.eu/helm/%s",
		msg.Player,
	)

	_, err := b.Session.WebhookExecute(
		b.Webhook.ID,
		b.Webhook.Token,
		false,
		&discordgo.WebhookParams{
			Username:  msg.Player,
			AvatarURL: avatarURL,
			Content:   msg.Message,
		},
	)
	if err != nil {
		stdlog.Printf("Failed to send message via webhook: %v", err)
	}
}

func ParseChatLine(line string) (*ChatMessage, bool) {
	if !strings.Contains(line, "<") || !strings.Contains(line, ">") {
		return nil, false
	}

	ignore := []string{
		"[Rcon]", "Disconnecting VANILLA connection attempt",
		"rejected vanilla connections", "lost connection", "id=<null>", "legacy=false",
		"lost connection: Disconnected", "<init>",
	}

	for _, p := range ignore {
		if strings.Contains(line, p) {
			return nil, false
		}
	}

	start := strings.Index(line, "<")
	end := strings.Index(line, ">")
	if start == -1 || end == -1 || end <= start {
		return nil, false
	}

	player := strings.TrimSpace(line[start+1 : end])
	msg := strings.TrimSpace(line[end+1:])

	if player == "" || msg == "" {
		return nil, false
	}

	return &ChatMessage{
		Player:  player,
		Message: msg,
	}, true
}
