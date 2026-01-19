package connections

import (
	"bytes"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
)

const imagePlayerCacheDir = "cache/players"

func GetPlayerImage(player string) (*bytes.Reader, string, error) {
	if err := os.MkdirAll(imagePlayerCacheDir, 0755); err != nil {
		return nil, "", err
	}

	filename := fmt.Sprintf("%s.png", sanitizePlayerFilename(player))
	path := filepath.Join(imagePlayerCacheDir, filename)

	if data, err := os.ReadFile(path); err == nil {
		return bytes.NewReader(data), filename, nil
	}

	url := fmt.Sprintf("https://mineskin.eu/helm/%s", player)

	resp, err := http.Get(url)
	if err != nil {
		return nil, "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, "", fmt.Errorf("erro ao baixar skin de %s: %s", player, resp.Status)
	}

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, "", err
	}

	if err := os.WriteFile(path, data, 0644); err != nil {
		return nil, "", err
	}

	return bytes.NewReader(data), filename, nil
}

func sanitizePlayerFilename(name string) string {
	return regexp.MustCompile(`[^\w\-]`).ReplaceAllString(name, "_")
}
