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

				// info do arquivo aberto
				curInfo, err := f.Stat()
				if err != nil {
					return
				}

				// posiciona no final (comportamento "tail -f")
				_, _ = f.Seek(0, io.SeekEnd)
				reader := bufio.NewReader(f)

				for {
					line, err := reader.ReadString('\n')
					if err != nil {
						if err == io.EOF {
							// checar se o arquivo no caminho foi substituído (rotacionado)
							pathInfo, statErr := os.Stat(w.Path)
							if statErr != nil {
								// caminho pode ter sumido temporariamente; esperar e continuar
								time.Sleep(100 * time.Millisecond)
								continue
							}

							// se não é o mesmo arquivo (inode diferente), houve rotação -> reabrir
							if !os.SameFile(curInfo, pathInfo) {
								// sair do loop para reabrir no próximo ciclo externo
								break
							}

							// se o arquivo foi truncado (size < current offset), seek pro início
							curOffset, _ := f.Seek(0, io.SeekCurrent)
							if pathInfo.Size() < curOffset {
								_, _ = f.Seek(0, io.SeekStart)
								reader = bufio.NewReader(f)
								curInfo = pathInfo
								continue
							}

							// caso normal: aguardar por novas linhas
							time.Sleep(100 * time.Millisecond)
							continue
						} else {
							// erro sério de leitura: sair para reabrir
							break
						}
					}

					// entregando linha para handlers
					for _, h := range w.Handlers {
						h(line)
					}
				}
			}(file)

			// pequena espera antes de tentar abrir novamente
			time.Sleep(200 * time.Millisecond)
		}
	}()
	return nil
}
