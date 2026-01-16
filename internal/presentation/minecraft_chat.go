package presentation

import (
	"fmt"
	stdlog "log"

	"discord-bot-go/internal/connections"
	"discord-bot-go/internal/log"

	"github.com/bwmarrin/discordgo"
)

type MinecraftChatBridge struct {
	Session   *discordgo.Session
	ChannelID string

	Webhook *discordgo.Webhook
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
	stdlog.Printf("Linha recebida do watcher: %s", line)
	msg, ok := log.ParseChatLine(line)
	if !ok {
		return
	}

	stdlog.Printf("Minecraft chat message from %s: %s", msg.Player, msg.Message)

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
