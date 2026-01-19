package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/bwmarrin/discordgo"
)

type RawStats map[string]any

type PlayerStats struct {
	Custom   map[string]any
	Mined    map[string]any
	Broken   map[string]any
	Crafted  map[string]any
	Used     map[string]any
	PickedUp map[string]any
	Dropped  map[string]any
	Killed   map[string]any
	KilledBy map[string]any
}

func parseFile(path string) (RawStats, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var raw RawStats
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, err
	}
	return raw, nil
}

func Load(folder, uuid string) (*PlayerStats, error) {
	path := filepath.Join(folder, fmt.Sprintf("%s.json", uuid))
	raw, err := parseFile(path)
	if err != nil {
		return nil, err
	}

	statsRaw, ok := raw["stats"].(map[string]any)
	if !ok {
		return &PlayerStats{}, nil
	}

	return &PlayerStats{
		Custom:   getMapSafe(statsRaw, "minecraft:custom"),
		Mined:    getMapSafe(statsRaw, "minecraft:mined"),
		Broken:   getMapSafe(statsRaw, "minecraft:broken"),
		Crafted:  getMapSafe(statsRaw, "minecraft:crafted"),
		Used:     getMapSafe(statsRaw, "minecraft:used"),
		PickedUp: getMapSafe(statsRaw, "minecraft:picked_up"),
		Dropped:  getMapSafe(statsRaw, "minecraft:dropped"),
		Killed:   getMapSafe(statsRaw, "minecraft:killed"),
		KilledBy: getMapSafe(statsRaw, "minecraft:killed_by"),
	}, nil
}

func getMapSafe(parent map[string]any, key string) map[string]any {
	if v, ok := parent[key]; ok {
		if m, ok := v.(map[string]any); ok {
			return m
		}
	}
	return map[string]any{}
}

func getFloatSafe(m map[string]any, key string) int {
	if v, ok := m[key]; ok {
		if f, ok := v.(float64); ok {
			return int(f)
		}
	}
	return 0
}

func Sum(m map[string]any) int {
	total := 0
	for _, v := range m {
		if n, ok := v.(float64); ok {
			total += int(n)
		}
	}
	return total
}

// --------------------
// BuildEmbed completo
// --------------------
func BuildEmbed(username string, ps *PlayerStats, apiURL string) *discordgo.MessageEmbed {
	playTime := getFloatSafe(ps.Custom, "minecraft:play_time") / 20
	deaths := getFloatSafe(ps.Custom, "minecraft:deaths")
	jumps := getFloatSafe(ps.Custom, "minecraft:jump")
	timeSinceDeath := getFloatSafe(ps.Custom, "minecraft:time_since_death") / 20
	damageDealt := getFloatSafe(ps.Custom, "minecraft:damage_dealt")
	damageTaken := getFloatSafe(ps.Custom, "minecraft:damage_taken")
	fishCaught := getFloatSafe(ps.Custom, "minecraft:fish_caught")

	walked := getFloatSafe(ps.Custom, "minecraft:walk_one_cm")
	sprinted := getFloatSafe(ps.Custom, "minecraft:sprint_one_cm")
	boat := getFloatSafe(ps.Custom, "minecraft:boat_one_cm")
	elytra := getFloatSafe(ps.Custom, "minecraft:aviate_one_cm")
	horse := getFloatSafe(ps.Custom, "minecraft:horse_one_cm")
	minecart := getFloatSafe(ps.Custom, "minecraft:minecart_one_cm")

	totalMined := Sum(ps.Mined)
	totalBroken := Sum(ps.Broken)
	totalCrafted := Sum(ps.Crafted)
	totalUsed := Sum(ps.Used)
	totalPickedUp := Sum(ps.PickedUp)
	totalDropped := Sum(ps.Dropped)
	totalKilled := Sum(ps.Killed)
	totalKilledBy := Sum(ps.KilledBy)

	// Mob mais morto
	mostKilledMob := ""
	mostKilledCount := 0
	for mob, count := range ps.Killed {
		n := 0
		if f, ok := count.(float64); ok {
			n = int(f)
		}
		if n > mostKilledCount {
			mostKilledCount = n
			mostKilledMob = mob
		}
	}
	// tradução do mob via API
	translatedMob := mostKilledMob
	if apiURL != "" && mostKilledMob != "" {
		translatedMob = fetchMobName(apiURL, mostKilledMob)
	}

	// Formatar distâncias em km e metros
	formatDistance := func(cm int) string {
		return fmt.Sprintf("%d km e %d metros", cm/100000, (cm%100000)/100)
	}

	embed := &discordgo.MessageEmbed{
		Title: fmt.Sprintf("Estatísticas de %s", username),
		Color: 0x7289DA,
		Fields: []*discordgo.MessageEmbedField{
			{
				Name: "Informações do Jogador",
				Value: fmt.Sprintf(
					"⏳ **Tempo jogado**: %dh %dm %ds\n"+
						"💀 **Mortes**: %d\n"+
						"⬆️ **Saltos**: %d\n"+
						"⏱️ **Tempo desde a última morte**: %dh %dm %ds",
					playTime/3600, (playTime%3600)/60, playTime%60,
					deaths,
					jumps,
					timeSinceDeath/3600, (timeSinceDeath%3600)/60, timeSinceDeath%60,
				),
				Inline: false,
			},
			{
				Name: "Itens",
				Value: fmt.Sprintf(
					"⛏️ **Blocos minerados**: %d\n"+
						"🔨 **Itens quebrados**: %d\n"+
						"🛠️ **Itens craftados**: %d\n"+
						"🔧 **Itens usados**: %d\n"+
						"📦 **Itens coletados**: %d\n"+
						"📤 **Itens dropados**: %d",
					totalMined, totalBroken, totalCrafted, totalUsed, totalPickedUp, totalDropped,
				),
				Inline: false,
			},
			{
				Name: "Ações",
				Value: fmt.Sprintf(
					"🗡️ **Mob mais morto:** %s (%d vezes)\n"+
						"⚔️ **Mobs mortos**: %d\n"+
						"💀 **Morreu contra Mobs**: %d\n"+
						"💥 **Dano causado**: %d\n"+
						"💔 **Dano sofrido**: %d\n"+
						"🐟 **Peixes pescados**: %d",
					translatedMob, mostKilledCount, totalKilled, totalKilledBy, damageDealt, damageTaken, fishCaught,
				),
				Inline: false,
			},
			{
				Name: "Transportes",
				Value: fmt.Sprintf(
					"🚶‍♂️ Andando: %s\n"+
						"🏃‍♂️ Correndo: %s\n"+
						"🚤 Barco: %s\n"+
						"🐎 Cavalo: %s\n"+
						"🕊️ Elytra: %s\n"+
						"🚆 Minecart: %s",
					formatDistance(walked),
					formatDistance(sprinted),
					formatDistance(boat),
					formatDistance(horse),
					formatDistance(elytra),
					formatDistance(minecart),
				),
				Inline: false,
			},
		},
	}

	return embed
}

// --------------------
// fetch do nome do mob via API
// --------------------
func fetchMobName(apiURL, mob string) string {
	mobName := strings.Split(mob, ":")
	if len(mobName) < 2 {
		return mob
	}
	name := strings.ReplaceAll(mobName[1], "_", " ")

	// Chamadas simples, sem async. Pode ser melhorado futuramente.
	resp, err := http.Get(fmt.Sprintf("%s/images/%s", apiURL, name))
	if err != nil {
		return name
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return name
	}

	var data map[string]any
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		return name
	}

	if n, ok := data["name"].(string); ok {
		return strings.ReplaceAll(n, "_", " ")
	}
	return name
}

func GetUUID(username string) (string, error) {
	resp, err := http.Get(fmt.Sprintf("https://api.mojang.com/users/profiles/minecraft/%s", username))
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return "", fmt.Errorf("player not found")
	}

	var data struct {
		ID string `json:"id"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		return "", err
	}

	return fmt.Sprintf("%s-%s-%s-%s-%s",
		data.ID[0:8],
		data.ID[8:12],
		data.ID[12:16],
		data.ID[16:20],
		data.ID[20:],
	), nil
}
