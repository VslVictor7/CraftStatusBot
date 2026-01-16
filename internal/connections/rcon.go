package connections

import (
	"fmt"
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
