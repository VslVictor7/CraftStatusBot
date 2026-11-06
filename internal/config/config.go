package config

import (
	"fmt"
	"net/url"
	"os"
	"strings"
)

type Config struct {
	DiscordToken    string
	StatusChannelID string
	StatusMessageID string
	EventsChannelID string
	ServerAddr      string
	Domain          string
	RCONAddr        string
	RCONPassword    string
	LogPath         string
	StatsFolder     string
	APIURL          string
}

func Load() (Config, error) {
	cfg := Config{
		DiscordToken:    os.Getenv("DISCORD_TOKEN"),
		StatusChannelID: os.Getenv("CHANNEL_ID"),
		StatusMessageID: os.Getenv("MESSAGE_ID"),
		EventsChannelID: os.Getenv("EVENTS_CHANNEL_ID"),
		ServerAddr:      os.Getenv("HOST"),
		Domain:          os.Getenv("DOMAIN"),
		RCONAddr:        os.Getenv("RCON_ADDR"),
		RCONPassword:    os.Getenv("RCON_PASSWORD"),
		LogPath:         os.Getenv("SERVER_LOG_PATH"),
		StatsFolder:     os.Getenv("STATS_FOLDER"),
		APIURL:          os.Getenv("API_URL"),
	}

	var missing []string
	for _, field := range []struct {
		name  string
		value string
	}{
		{"DISCORD_TOKEN", cfg.DiscordToken},
		{"CHANNEL_ID", cfg.StatusChannelID},
		{"MESSAGE_ID", cfg.StatusMessageID},
		{"EVENTS_CHANNEL_ID", cfg.EventsChannelID},
		{"HOST", cfg.ServerAddr},
		{"RCON_ADDR", cfg.RCONAddr},
		{"RCON_PASSWORD", cfg.RCONPassword},
		{"SERVER_LOG_PATH", cfg.LogPath},
		{"STATS_FOLDER", cfg.StatsFolder},
		{"API_URL", cfg.APIURL},
	} {
		if strings.TrimSpace(field.value) == "" {
			missing = append(missing, field.name)
		}
	}
	if len(missing) > 0 {
		return Config{}, fmt.Errorf("variáveis de ambiente obrigatórias ausentes: %s", strings.Join(missing, ", "))
	}

	apiURL, err := url.Parse(cfg.APIURL)
	if err != nil || (apiURL.Scheme != "http" && apiURL.Scheme != "https") || apiURL.Hostname() == "" {
		return Config{}, fmt.Errorf("API_URL deve ser uma URL HTTP ou HTTPS válida")
	}
	if strings.TrimSpace(cfg.Domain) == "" {
		cfg.Domain = cfg.ServerAddr
	}
	return cfg, nil
}
