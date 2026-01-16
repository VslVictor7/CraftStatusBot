package log

import (
	"strings"
)

type ChatMessage struct {
	Player  string
	Message string
}

func ParseChatLine(line string) (*ChatMessage, bool) {
	if !strings.Contains(line, "<") || !strings.Contains(line, ">") {
		return nil, false
	}

	ignore := []string{
		"[Rcon]", "Disconnecting VANILLA connection attempt",
		"rejected vanilla connections", "lost connection", "id=<null>", "legacy=false",
		"lost connection: Disconnected", "<init>",
	}

	for _, p := range ignore {
		if strings.Contains(line, p) {
			return nil, false
		}
	}

	start := strings.Index(line, "<")
	end := strings.Index(line, ">")
	if start == -1 || end == -1 || end <= start {
		return nil, false
	}

	player := strings.TrimSpace(line[start+1 : end])
	msg := strings.TrimSpace(line[end+1:])

	if player == "" || msg == "" {
		return nil, false
	}

	return &ChatMessage{
		Player:  player,
		Message: msg,
	}, true
}
