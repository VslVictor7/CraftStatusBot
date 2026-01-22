package handlers

import (
	"github.com/bwmarrin/discordgo"
)

type CommandLogPayload struct {
	Command   string       `json:"command"`
	MemberID  string       `json:"memberId"`
	Arguments []CommandArg `json:"arguments"`
}

type CommandArg struct {
	Name  string `json:"name"`
	Value string `json:"value"`
}

func BuildCommandLog(i *discordgo.InteractionCreate) CommandLogPayload {
	data := i.ApplicationCommandData()

	args := []CommandArg{}
	for _, opt := range data.Options {
		args = append(args, CommandArg{
			Name:  opt.Name,
			Value: opt.StringValue(),
		})
	}

	memberID := ""
	if i.Member != nil && i.Member.User != nil {
		memberID = i.Member.User.ID
	}

	return CommandLogPayload{
		Command:   data.Name,
		MemberID:  memberID,
		Arguments: args,
	}
}
