package commands

import "github.com/bwmarrin/discordgo"

var PingCommand = &discordgo.ApplicationCommand{
	Name:        "ping",
	Description: "Responde com pong",
}

func PingHandler(s *discordgo.Session, i *discordgo.InteractionCreate) {
	if i.ApplicationCommandData().Name != "ping" {
		return
	}

	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "pong noob lixo",
		},
	})
}
