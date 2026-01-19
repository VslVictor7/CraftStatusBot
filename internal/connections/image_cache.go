package connections

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
)

const imageCacheDir = "cache/mobs"

func GetMobImage(mob string) (*bytes.Reader, string, error) {
	if err := os.MkdirAll(imageCacheDir, 0755); err != nil {
		return nil, "", err
	}

	filename := fmt.Sprintf("%s.png", sanitizeFilename(mob))
	path := filepath.Join(imageCacheDir, filename)

	if _, err := os.Stat(path); err == nil {
		data, err := os.ReadFile(path)
		return bytes.NewReader(data), filename, err
	}

	apiURL := os.Getenv("API_URL")
	if apiURL == "" {
		return nil, "", fmt.Errorf("API_URL não definida")
	}

	metaResp, err := http.Get(fmt.Sprintf("%s/images/%s", apiURL, mob))
	if err != nil {
		return nil, "", err
	}
	defer metaResp.Body.Close()

	var meta struct {
		URL string `json:"url"`
	}
	if err := json.NewDecoder(metaResp.Body).Decode(&meta); err != nil {
		return nil, "", err
	}

	if meta.URL == "" {
		return nil, "", fmt.Errorf("URL da imagem vazia para mob %s", mob)
	}

	imgResp, err := http.Get(meta.URL)
	if err != nil {
		return nil, "", err
	}
	defer imgResp.Body.Close()

	data, err := io.ReadAll(imgResp.Body)
	if err != nil {
		return nil, "", err
	}

	if err := os.WriteFile(path, data, 0644); err != nil {
		return nil, "", err
	}

	return bytes.NewReader(data), filename, nil
}

func sanitizeFilename(name string) string {
	return regexp.MustCompile(`[^\w\-]`).ReplaceAllString(name, "_")
}
