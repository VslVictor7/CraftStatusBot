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

			openedInfo, err := file.Stat()
			if err != nil {
				file.Close()
				time.Sleep(200 * time.Millisecond)
				continue
			}

			_, _ = file.Seek(0, io.SeekEnd)
			reader := bufio.NewReader(file)

			for {
				line, err := reader.ReadString('\n')
				if err != nil {
					if err == io.EOF {
						currentInfo, statErr := os.Stat(w.Path)
						if statErr != nil {
							file.Close()
							time.Sleep(200 * time.Millisecond)
							break
						}

						// Reopen when the path now points to a different file (rotation).
						if !os.SameFile(openedInfo, currentInfo) {
							file.Close()
							time.Sleep(100 * time.Millisecond)
							break
						}

						// Handle in-place truncation (copytruncate style rotation).
						pos, seekErr := file.Seek(0, io.SeekCurrent)
						if seekErr == nil && currentInfo.Size() < pos {
							_, _ = file.Seek(0, io.SeekStart)
							reader = bufio.NewReader(file)
							continue
						}

						time.Sleep(100 * time.Millisecond)
						continue
					}
					file.Close()
					time.Sleep(200 * time.Millisecond)
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
