package presentation

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"regexp"
	"sort"
	"strings"

	"discord-bot-go/internal/connections"

	"github.com/bwmarrin/discordgo"
)

var (
	namedRegex = regexp.MustCompile(`Named entity (\w+)\['([^']+)'`)
	villagerRe = regexp.MustCompile(`\bVillager\b`)
	coordsRe   = regexp.MustCompile(`x=(-?\d+\.\d+), y=(-?\d+\.\d+), z=(-?\d+\.\d+)`)
)

type DeathPattern struct {
	Pattern string
	Message string
}

func ProcessMobDeath(line string, s *discordgo.Session, channelID string) {
	if shouldIgnore(line) {
		return
	}

	mobType, mobName, isVillager := extractMob(line)
	if mobName == "" {
		return
	}

	deaths, mobs := fetchMaps()

	pattern, message := matchDeath(line, deaths)
	if pattern == "" {
		return
	}

	entity, item := extractEntityAndItem(line, pattern)
	entity = translateMobDeaths(entity, mobs)
	item = translateMobDeaths(item, mobs)

	msg := strings.ReplaceAll(message, "{entity}", entity)
	if strings.Contains(msg, "{item}") && item != "" {
		msg = strings.ReplaceAll(msg, "{item}", "["+item+"]")
	}

	reader, filename, err := connections.GetMobImage(resolveMobName(mobType, isVillager))
	if err != nil {
		return
	}

	coords := extractCoords(line)

	sendEmbed(s, channelID, mobName, msg, coords, reader, filename)
}

func shouldIgnore(line string) bool {
	ignore := []string{
		"[Rcon]",
		"lost connection",
		"<init>",
	}
	for _, i := range ignore {
		if strings.Contains(line, i) {
			return true
		}
	}
	return false
}

func extractMob(line string) (mobType string, mobName string, isVillager bool) {
	if m := namedRegex.FindStringSubmatch(line); m != nil {
		return m[1], m[2], false
	}
	if villagerRe.MatchString(line) {
		return "Villager", "Villager", true
	}
	return "", "", false
}

func extractCoords(line string) string {
	m := coordsRe.FindStringSubmatch(line)
	if m == nil {
		return ""
	}
	return fmt.Sprintf("(x: %s, y: %s, z: %s)", m[1], m[2], m[3])
}

func fetchMaps() ([]DeathPattern, map[string]string) {
	api := os.Getenv("API_URL")
	return fetchDeaths(api + "/deaths"), fetchMobMap(api + "/mobs")
}

func fetchMobMap(url string) map[string]string {
	resp, _ := http.Get(url)
	if resp == nil {
		return map[string]string{}
	}
	defer resp.Body.Close()

	var data map[string]string
	json.NewDecoder(resp.Body).Decode(&data)
	return data
}

func fetchDeaths(url string) []DeathPattern {
	resp, _ := http.Get(url)
	if resp == nil {
		return nil
	}
	defer resp.Body.Close()

	raw := map[string]string{}
	json.NewDecoder(resp.Body).Decode(&raw)

	ordered := make([]DeathPattern, 0, len(raw))
	for p, m := range raw {
		ordered = append(ordered, DeathPattern{
			Pattern: p,
			Message: m,
		})
	}

	sort.SliceStable(ordered, func(i, j int) bool {
		return strings.Count(ordered[i].Pattern, "{") >
			strings.Count(ordered[j].Pattern, "{")
	})

	return ordered
}

func matchDeath(line string, deaths []DeathPattern) (string, string) {
	for _, d := range deaths {
		r := regexp.QuoteMeta(d.Pattern)
		r = strings.ReplaceAll(r, "\\{player\\}", ".+")
		r = strings.ReplaceAll(r, "\\{entity\\}", "(.+)")
		r = strings.ReplaceAll(r, "\\{item\\}", `\[([^\]]+)\]`)

		re := regexp.MustCompile(r)
		if re.MatchString(line) {
			return r, d.Message
		}
	}
	return "", ""
}

func extractEntityAndItem(line, pattern string) (string, string) {
	re := regexp.MustCompile(pattern)
	m := re.FindStringSubmatch(line)

	var entity, item string
	if len(m) > 1 {
		entity = m[1]
	}
	if len(m) > 2 {
		item = m[2]
	}
	return entity, item
}

func translateMobDeaths(raw string, mobs map[string]string) string {
	if v, ok := mobs[strings.TrimSpace(raw)]; ok {
		return v
	}
	return raw
}

func sendEmbed(
	s *discordgo.Session,
	ch, name, msg, coords string,
	reader io.Reader,
	filename string,
) {
	file := &discordgo.File{
		Name:   filename,
		Reader: reader,
	}

	embed := &discordgo.MessageEmbed{
		Author: &discordgo.MessageEmbedAuthor{
			Name:    name + " " + msg,
			IconURL: "attachment://" + filename,
		},
		Color: 0x000000,
	}

	if coords != "" {
		embed.Footer = &discordgo.MessageEmbedFooter{
			Text: coords,
		}
	}

	s.ChannelMessageSendComplex(ch, &discordgo.MessageSend{
		Files: []*discordgo.File{file},
		Embed: embed,
	})
}

func resolveMobName(mob string, isVillager bool) string {
	if isVillager {
		return "Villager"
	}
	return mob
}
