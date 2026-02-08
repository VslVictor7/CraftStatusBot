package connections

import (
	"fmt"
	"strings"
	"sync"

	"github.com/gorcon/rcon"
)

type Chat struct {
	Addr     string
	Password string

	mu   sync.Mutex
	conn *rcon.Conn
}

func (c *Chat) Connect() error {
	conn, err := rcon.Dial(c.Addr, c.Password)
	if err != nil {
		return err
	}
	c.conn = conn
	return nil
}

func (c *Chat) Close() {
	if c.conn != nil {
		_ = c.conn.Close()
	}
}

func (c *Chat) Say(message string) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.conn == nil {
		return fmt.Errorf("RCON não conectado")
	}

	_, err := c.conn.Execute("say " + message)
	return err
}

func (c *Chat) Tellraw(json string) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.conn == nil {
		return fmt.Errorf("RCON não conectado")
	}

	cmd := fmt.Sprintf("tellraw @a %s", json)
	_, err := c.conn.Execute(cmd)
	return err
}

func (c *Chat) ListPlayers() ([]string, error) {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.conn == nil {
		return nil, fmt.Errorf("RCON não conectado")
	}

	resp, err := c.conn.Execute("list")
	if err != nil {
		return nil, err
	}

	parts := strings.Split(resp, ":")
	if len(parts) < 2 {
		return []string{}, nil
	}

	raw := strings.TrimSpace(parts[1])
	if raw == "" {
		return []string{}, nil
	}

	names := strings.Split(raw, ", ")
	return names, nil
}
