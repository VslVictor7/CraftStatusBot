package connections

import "github.com/bwmarrin/discordgo"

func EnsureWebhook(
	s *discordgo.Session,
	channelID string,
	name string,
) (*discordgo.Webhook, error) {

	webhooks, err := s.ChannelWebhooks(channelID)
	if err != nil {
		return nil, err
	}

	for _, wh := range webhooks {
		if wh.Name == name {
			return wh, nil
		}
	}

	return s.WebhookCreate(channelID, name, "")
}
