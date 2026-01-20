package server

import (
	"fmt"
	"time"
)

type ServerMonitor struct {
	ServerAddr string
	Interval   time.Duration

	StatusEmbed *StatusEmbed

	lastNames []string
}

func (m *ServerMonitor) Start() {
	go func() {
		for {
			snapshot, err := CollectSnapshot(m.ServerAddr)
			if err != nil {
				fmt.Printf("[ERROR] Falha ao coletar snapshot do servidor %s: %v\n, Tentando novamente em 1 minuto...", m.ServerAddr, err)
			}

			// reconciliar nomes
			reconciledNames := reconcileNames(
				m.lastNames,
				snapshot.PlayerNames,
				snapshot.PlayerCount,
			)
			snapshot.PlayerNames = reconciledNames
			m.lastNames = reconciledNames

			// atualizar embed
			if m.StatusEmbed != nil {
				m.StatusEmbed.Update(snapshot)
			}

			// definir sleep dinâmico
			sleepDuration := m.Interval
			if !snapshot.Online {
				sleepDuration = 1 * time.Minute
			}

			time.Sleep(sleepDuration)
		}
	}()
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
