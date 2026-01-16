package commands

import "github.com/bwmarrin/discordgo"

type Ping struct{}

func (p *Ping) Name() string {
	return "ping"
}

func (p *Ping) Command() *discordgo.ApplicationCommand {
	return &discordgo.ApplicationCommand{
		Name:        p.Name(),
		Description: "Responde com pong",
	}
}

func (p *Ping) Handler(s *discordgo.Session, i *discordgo.InteractionCreate) {
	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "pong",
		},
	})
}

func init() {
	cmd := &Ping{}
	RegisteredCommands[cmd.Name()] = cmd
}
