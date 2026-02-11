package log

import (
	"bufio"
	"io"
	"os"
	"time"
)

type Handler func(line string)

type Watcher struct {
	Path     string
	Handlers []Handler
}

func New(path string) *Watcher {
	return &Watcher{Path: path}
}

func (w *Watcher) Register(h Handler) {
	w.Handlers = append(w.Handlers, h)
}

func (w *Watcher) Start() error {
	go func() {
		for {
			file, err := os.Open(w.Path)
			if err != nil {
				time.Sleep(500 * time.Millisecond)
				continue
			}

			reader := bufio.NewReader(file)

			// começa no final (tail -F)
			_, _ = file.Seek(0, io.SeekEnd)

			for {
				line, err := reader.ReadString('\n')
				if err != nil {
					// qualquer erro → fecha e reabre
					file.Close()
					time.Sleep(100 * time.Millisecond)
					break
				}

				for _, h := range w.Handlers {
					h(line)
				}
			}
		}
	}()
	return nil
}
