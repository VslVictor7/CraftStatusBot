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
				time.Sleep(1 * time.Second)
				continue
			}

			func(f *os.File) {
				defer f.Close()

				f.Seek(0, io.SeekEnd)
				reader := bufio.NewReader(f)

				for {
					line, err := reader.ReadString('\n')
					if err != nil {
						if err == io.EOF {
							time.Sleep(100 * time.Millisecond)
							continue
						} else {
							break
						}
					}

					for _, h := range w.Handlers {
						h(line)
					}
				}
			}(file)

			time.Sleep(1 * time.Second)
		}
	}()
	return nil
}
