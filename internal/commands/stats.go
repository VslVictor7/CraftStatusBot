package commands

import (
	"os"

	"discord-bot-go/internal/commands/handlers"

	"github.com/bwmarrin/discordgo"
)

type Stats struct{}

func (c *Stats) Name() string {
	return "stats"
}

func (c *Stats) Command() *discordgo.ApplicationCommand {
	return &discordgo.ApplicationCommand{
		Name:        "stats",
		Description: "Mostra estatísticas de um jogador Minecraft",
		Options: []*discordgo.ApplicationCommandOption{
			{
				Type:        discordgo.ApplicationCommandOptionString,
				Name:        "username",
				Description: "Nome do jogador",
				Required:    true,
			},
		},
	}
}

func (c *Stats) Handler(s *discordgo.Session, i *discordgo.InteractionCreate) {
	username := i.ApplicationCommandData().Options[0].StringValue()
	statsFolder := os.Getenv("STATS_FOLDER")

	uuid, err := handlers.GetUUID(username)
	if err != nil {
		respondEphemeral(s, i, "Jogador não encontrado.")
		return
	}

	playerStats, err := handlers.Load(statsFolder, uuid)
	if err != nil {
		respondEphemeral(s, i, "Erro ao carregar estatísticas.")
		return
	}

	embed := handlers.BuildEmbed(username, playerStats)

	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Embeds: []*discordgo.MessageEmbed{embed},
		},
	})
}

func respondEphemeral(s *discordgo.Session, i *discordgo.InteractionCreate, msg string) {
	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: msg,
			Flags:   discordgo.MessageFlagsEphemeral,
		},
	})
}

func init() {
	cmd := &Stats{}
	RegisteredCommands[cmd.Name()] = cmd
}
