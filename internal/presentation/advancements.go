package presentation

import (
	"discord-bot-go/internal/connections"
	"discord-bot-go/internal/log"
	"fmt"
	"strings"

	"github.com/bwmarrin/discordgo"
)

func ProcessAdvancementLine(s *discordgo.Session, channelID string, line string) {
	ignorePatterns := []string{
		"[Rcon]", "[Not Secure]", "Disconnecting VANILLA connection attempt",
		"rejected vanilla connections", "lost connection", "id=<null>", "legacy=false",
		"lost connection: Disconnected", "<init>", "<", ">",
	}

	for _, pat := range ignorePatterns {
		if strings.Contains(line, pat) {
			return
		}
	}

	playerName, message, eventName := extractPlayerMessage(line)
	if playerName == "" || message == "" || eventName == "" {
		return
	}

	var color int
	var action string

	if strings.Contains(message, "has reached the goal") {
		color = 0xFFA500
		action = "alcançou um objetivo:"
	} else if strings.Contains(message, "has made the advancement") {
		color = 0x0000FF
		action = "obteve um avanço:"
	} else if strings.Contains(message, "has completed the challenge") {
		color = 0x800080
		action = "completou um desafio:"
	} else {
		return
	}

	sendPlayerEvent(s, channelID, playerName, action, eventName, color)
}

func extractPlayerMessage(logLine string) (string, string, string) {
	parts := strings.SplitN(logLine, "]: ", 2)
	if len(parts) < 2 {
		return "", "", ""
	}

	msgPart := parts[1]

	playerEnd := strings.Index(msgPart, " has ")
	if playerEnd == -1 {
		return "", "", ""
	}
	playerName := msgPart[:playerEnd]

	message := msgPart[playerEnd:]
	eventStart := strings.Index(msgPart, "[")
	eventEnd := strings.Index(msgPart, "]")
	if eventStart == -1 || eventEnd == -1 || eventEnd <= eventStart {
		return playerName, message, ""
	}
	eventName := msgPart[eventStart+1 : eventEnd]

	return playerName, message, eventName
}

func sendPlayerEvent(
	s *discordgo.Session,
	channelID string,
	playerName string,
	action string,
	eventName string,
	color int,
) {
	reader, filename, err := connections.GetPlayerImage(playerName)
	if err != nil {
		log.LogError("Falha ao obter imagem do player:", err)
		return
	}

	file := &discordgo.File{
		Name:   filename,
		Reader: reader,
	}

	embed := &discordgo.MessageEmbed{
		Color: color,
		Author: &discordgo.MessageEmbedAuthor{
			Name:    fmt.Sprintf("%s %s %s", playerName, action, eventName),
			IconURL: "attachment://" + filename,
		},
	}

	_, err = s.ChannelMessageSendComplex(
		channelID,
		&discordgo.MessageSend{
			Embed: embed,
			Files: []*discordgo.File{file},
		},
	)

	if err != nil {
		log.LogError("Falha ao enviar evento do jogador:", err)
		return
	}
}
