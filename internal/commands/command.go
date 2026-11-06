package commands

import "github.com/bwmarrin/discordgo"

type Command interface {
	Name() string
	Command() *discordgo.ApplicationCommand
	Handler(s *discordgo.Session, i *discordgo.InteractionCreate)
}

func New(statsFolder, apiURL string) map[string]Command {
	stats := &Stats{StatsFolder: statsFolder, APIURL: apiURL}
	ranking := &Ranking{StatsFolder: statsFolder}
	return map[string]Command{
		stats.Name():   stats,
		ranking.Name(): ranking,
	}
}
