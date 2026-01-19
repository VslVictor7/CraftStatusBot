package commands

import "github.com/bwmarrin/discordgo"

type Command interface {
	Name() string
	Command() *discordgo.ApplicationCommand
	Handler(s *discordgo.Session, i *discordgo.InteractionCreate)
}

var RegisteredCommands = map[string]Command{}
