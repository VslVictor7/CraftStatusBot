package server

import (
	"fmt"
	"sort"
	"strings"
	"time"

	"discord-bot-go/internal/handshake"

	"github.com/bwmarrin/discordgo"
)

type ServerMonitor struct {
	Session    *discordgo.Session
	ChannelID  string
	MessageID  string
	ServerAddr string
	BotName    string
	Interval   time.Duration

	lastState *serverState
}

type serverState struct {
	Online        bool
	PlayersOnline int
	Version       string
	PlayerNames   []string
}

// Start inicia o loop em background
func (m *ServerMonitor) Start() {
	go func() {
		for {
			m.tick()
			time.Sleep(m.Interval)
		}
	}()
}

func (m *ServerMonitor) tick() {
	res, err := handshake.ResolveServerStatus(m.ServerAddr, 5*time.Minute)
	if err != nil {
		m.update(false, 0, "Desconhecido", nil)
		return
	}

	status, err := handshake.Ping(res, 3*time.Second)
	if err != nil {
		m.update(false, 0, "Desconhecido", nil)
		return
	}

	var names []string
	for _, p := range status.Players.Sample {
		names = append(names, p.Name)
	}
	sort.Strings(names)

	m.update(
		true,
		status.Players.Online,
		status.Version.Name,
		names,
	)
}

func (m *ServerMonitor) update(
	online bool,
	players int,
	version string,
	names []string,
) {
	state := &serverState{
		Online:        online,
		PlayersOnline: players,
		Version:       version,
		PlayerNames:   names,
	}

	if m.lastState != nil && !hasChanged(m.lastState, state) {
		return
	}

	embed := BuildServerEmbed(
		online,
		players,
		version,
		names,
		m.BotName,
	)

	_, err := m.Session.ChannelMessageEditEmbed(
		m.ChannelID,
		m.MessageID,
		embed,
	)
	if err != nil {
		fmt.Println("erro ao atualizar embed:", err)
		return
	}

	m.lastState = state
}

func hasChanged(a, b *serverState) bool {
	if a.Online != b.Online {
		return true
	}
	if a.PlayersOnline != b.PlayersOnline {
		return true
	}
	if strings.Join(a.PlayerNames, ",") != strings.Join(b.PlayerNames, ",") {
		return true
	}
	if a.Version != b.Version {
		return true
	}
	return false
}
