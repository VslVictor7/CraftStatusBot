package server

import "time"

type ServerMonitor struct {
	ServerAddr string
	Interval   time.Duration

	StatusEmbed  *StatusEmbed
	PlayerEvents *PlayerEvents

	lastNames []string
}

func (m *ServerMonitor) Start() {
	go func() {
		for {
			m.tick()
			time.Sleep(m.Interval)
		}
	}()
}

func (m *ServerMonitor) tick() {
	snapshot, _ := CollectSnapshot(m.ServerAddr)

	reconciledNames := reconcileNames(
		m.lastNames,
		snapshot.PlayerNames,
		snapshot.PlayerCount,
	)

	snapshot.PlayerNames = reconciledNames
	m.lastNames = reconciledNames

	if m.StatusEmbed != nil {
		m.StatusEmbed.Update(snapshot)
	}

	if m.PlayerEvents != nil {
		m.PlayerEvents.Update(snapshot)
	}
}

func reconcileNames(
	prev []string,
	current []string,
	playerCount int,
) []string {

	if playerCount == 0 {
		return []string{}
	}

	if len(current) <= playerCount {
		return current
	}

	if len(prev) == 0 {
		return current[:playerCount]
	}

	var result []string
	for _, name := range prev {
		if contains(current, name) {
			result = append(result, name)
		}
	}

	if len(result) > playerCount {
		return result[:playerCount]
	}

	return result
}

func contains(slice []string, value string) bool {
	for _, v := range slice {
		if v == value {
			return true
		}
	}
	return false
}
