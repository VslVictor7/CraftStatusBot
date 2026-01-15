package commands

import "github.com/bwmarrin/discordgo"

type Hello struct{}

func (h *Hello) Name() string {
	return "hello"
}

func (h *Hello) Command() *discordgo.ApplicationCommand {
	return &discordgo.ApplicationCommand{
		Name:        "hello",
		Description: "Diz olá",
	}
}

func (h *Hello) Handler(s *discordgo.Session, i *discordgo.InteractionCreate) {
	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "Ola noob",
		},
	})
}

func init() {
	cmd := &Hello{}
	RegisteredCommands[cmd.Name()] = cmd
}
