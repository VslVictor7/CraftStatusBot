package presentation

import (
	"discord-bot-go/internal/connections"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"regexp"
	"strings"
	"sync"

	"github.com/bwmarrin/discordgo"
)

var (
	deathMessages map[string]string
	mobsMap       map[string]string
	loadOnce      sync.Once
)

func loadDeathData() {
	apiURL := os.Getenv("API_URL")

	deathMessages = fetchMap(apiURL + "/deaths")
	mobsMap = fetchMap(apiURL + "/mobs")
}

func fetchMap(url string) map[string]string {
	resp, err := http.Get(url)
	if err != nil {
		fmt.Println("[ERROR] API error:", err)
		return map[string]string{}
	}
	defer resp.Body.Close()

	var data map[string]string
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		fmt.Println("[ERROR] Decode error:", err)
		return map[string]string{}
	}
	return data
}

func ProcessDeathLine(s *discordgo.Session, channelID, line string) {
	ignorePatterns := []string{
		"[Rcon]", "[Not Secure]", "Disconnecting VANILLA connection attempt",
		"rejected vanilla connections", "lost connection", "id=<null>",
		"legacy=false", "lost connection: Disconnected",
		"<init>", "<", ">", "x=", "y=", "z=",
	}

	for _, pat := range ignorePatterns {
		if strings.Contains(line, pat) {
			return
		}
	}

	loadOnce.Do(loadDeathData)

	for pattern, translated := range deathMessages {
		regex := buildDeathRegex(pattern)
		re := regexp.MustCompile(regex)

		match := re.FindStringSubmatch(line)
		if match == nil {
			continue
		}

		groups := map[string]string{}
		for i, name := range re.SubexpNames() {
			if i > 0 && name != "" {
				groups[name] = match[i]
			}
		}

		player := groups["player"]
		entity := translate(groups["entity"])
		item := translate(groups["item"])

		msg := translated
		msg = strings.ReplaceAll(msg, "{entity}", entity)
		msg = strings.ReplaceAll(msg, "{item}", fmt.Sprintf("[%s]", item))

		sendDeathEvent(s, channelID, player, msg)
		return
	}
}

func buildDeathRegex(pattern string) string {
	r := regexp.QuoteMeta(pattern)

	r = strings.ReplaceAll(r, "\\{player\\}", `(?P<player>\S+)`)
	r = strings.ReplaceAll(r, "\\{entity\\}", `(?P<entity>.+?)`)
	r = strings.ReplaceAll(
		r,
		"\\{item\\}",
		`\[(?P<item>[^\[\]]+)\]`,
	)

	return r
}

func translate(raw string) string {
	if raw == "" {
		return "desconhecido"
	}
	if v, ok := mobsMap[strings.TrimSpace(raw)]; ok {
		return v
	}
	return raw
}

func sendDeathEvent(s *discordgo.Session, channelID, player, message string) {
	reader, filename, err := connections.GetPlayerImage(player)
	if err != nil {
		fmt.Println("[ERROR] Falha ao obter imagem do player:", err)
		return
	}

	file := &discordgo.File{
		Name:   filename,
		Reader: reader,
	}

	embed := &discordgo.MessageEmbed{
		Color: 0x000000,
		Author: &discordgo.MessageEmbedAuthor{
			Name:    fmt.Sprintf("%s %s", player, message),
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
		fmt.Println("[ERROR] Erro ao enviar evento de morte:", err)
	}
}
