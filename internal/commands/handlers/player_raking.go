package handlers

import (
	"encoding/json"
	"fmt"
	"io/fs"
	"net/http"
	"os"
	"path/filepath"
	"sort"
)

type PlayerTime struct {
	UUID     string
	Username string
	PlayTime int
}

func GetAllPlayerTimes(folder string) ([]PlayerTime, error) {
	var result []PlayerTime

	err := filepath.WalkDir(folder, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() || filepath.Ext(d.Name()) != ".json" {
			return nil
		}

		data, err := os.ReadFile(path)
		if err != nil {
			return nil
		}

		var raw map[string]any
		if err := json.Unmarshal(data, &raw); err != nil {
			return nil
		}

		stats, ok := raw["stats"].(map[string]any)
		if !ok {
			return nil
		}

		custom := GetMapSafe(stats, "minecraft:custom")
		playTime := GetFloatSafe(custom, "minecraft:play_time") / 20

		uuid := d.Name()[:len(d.Name())-len(filepath.Ext(d.Name()))]
		username, _ := GetUsernameFromUUID(uuid)

		result = append(result, PlayerTime{
			UUID:     uuid,
			Username: username,
			PlayTime: playTime,
		})

		return nil
	})

	if err != nil {
		return nil, fmt.Errorf("falha ao ler diretório de stats: %w", err)
	}

	sort.Slice(result, func(i, j int) bool {
		return result[i].PlayTime > result[j].PlayTime
	})

	return result, nil
}

func GetUsernameFromUUID(uuid string) (string, error) {
	resp, err := http.Get(fmt.Sprintf("https://api.minetools.eu/uuid/%s", uuid))
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return "", fmt.Errorf("UUID não encontrado")
	}

	var data struct {
		Name string `json:"name"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		return "", err
	}

	return data.Name, nil
}

func GetMapSafe(parent map[string]any, key string) map[string]any {
	if v, ok := parent[key]; ok {
		if m, ok := v.(map[string]any); ok {
			return m
		}
	}
	return map[string]any{}
}

func GetFloatSafe(m map[string]any, key string) int {
	if v, ok := m[key]; ok {
		if f, ok := v.(float64); ok {
			return int(f)
		}
	}
	return 0
}
