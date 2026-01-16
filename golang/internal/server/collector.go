package server

import (
	"sort"
	"time"

	"discord-bot-go/internal/connections"
)

type ServerSnapshot struct {
	Online      bool
	PlayerCount int
	Version     string
	PlayerNames []string
	CollectedAt time.Time
}

func CollectSnapshot(serverAddr string) (*ServerSnapshot, error) {

	res, err := connections.ResolveServerStatus(serverAddr, 5*time.Minute)
	if err != nil {
		return &ServerSnapshot{
			Online:      false,
			CollectedAt: time.Now(),
		}, err
	}

	status, err := connections.Ping(res, 3*time.Second)
	if err != nil {
		return &ServerSnapshot{
			Online:      false,
			CollectedAt: time.Now(),
		}, err
	}

	var names []string
	for _, p := range status.Players.Sample {
		names = append(names, p.Name)
	}
	sort.Strings(names)

	return &ServerSnapshot{
		Online:      true,
		PlayerCount: status.Players.Online,
		Version:     status.Version.Name,
		PlayerNames: names,
		CollectedAt: time.Now(),
	}, nil
}
