package commands

import (
	"fmt"
	"os"
	"time"

	"discord-bot-go/internal/commands/handlers"

	"github.com/bwmarrin/discordgo"
)

type Ranking struct{}

func (r *Ranking) Name() string {
	return "ranking"
}

func (r *Ranking) Command() *discordgo.ApplicationCommand {
	return &discordgo.ApplicationCommand{
		Name:        r.Name(),
		Description: "Mostra o ranking dos jogadores com mais tempo de jogo",
	}
}

func (r *Ranking) Handler(s *discordgo.Session, i *discordgo.InteractionCreate) {
	statsFolder := os.Getenv("STATS_FOLDER")
	topN := 5

	playerTimes, err := handlers.GetAllPlayerTimes(statsFolder)
	if err != nil || len(playerTimes) == 0 {
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Content: "Nenhum jogador encontrado.",
			},
		})
		return
	}

	if len(playerTimes) < topN {
		topN = len(playerTimes)
	}

	embed := &discordgo.MessageEmbed{
		Title:     "Ranking dos Jogadores com Mais Tempo de Jogo",
		Color:     0xFFFF00,
		Timestamp: time.Now().Format(time.RFC3339),
		Fields:    []*discordgo.MessageEmbedField{},
	}

	medals := map[int]string{1: "🥇", 2: "🥈", 3: "🥉"}

	for rank, pt := range playerTimes[:topN] {
		h := pt.PlayTime / 3600
		m := (pt.PlayTime % 3600) / 60
		sSec := pt.PlayTime % 60

		embed.Fields = append(embed.Fields, &discordgo.MessageEmbedField{
			Name:   fmt.Sprintf("%dº Lugar %s", rank+1, medals[rank+1]),
			Value:  fmt.Sprintf("Nome: %s\nTempo jogado: %dh %dm %ds", pt.Username, h, m, sSec),
			Inline: false,
		})
	}

	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Embeds: []*discordgo.MessageEmbed{embed},
		},
	})
}

func init() {
	cmd := &Ranking{}
	RegisteredCommands[cmd.Name()] = cmd
}
