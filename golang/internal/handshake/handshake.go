package handshake

import (
	"bufio"
	"bytes"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"
)

var resolveCache = map[string]*CachedResolution{}
var resolveMu sync.Mutex

// ===== Modelo do Status =====

type StatusSlim struct {
	Version struct {
		Name string `json:"name"`
	} `json:"version"`

	Players struct {
		Max    int `json:"max"`
		Online int `json:"online"`
		Sample []struct {
			Name string `json:"name"`
		} `json:"sample"`
	} `json:"players"`
}

// ===== Estrutura de destino resolvido e cache =====

type ResolvedAddress struct {
	LogicalHost string
	Host        string
	Port        uint16
}

type CachedResolution struct {
	Resolved *ResolvedAddress
	IPs      []net.IP
	Expires  time.Time
}

var bufferPool = sync.Pool{
	New: func() any {
		return new(bytes.Buffer)
	},
}

// ===== Resolver de endereço (SRV + fallback) =====

func ResolveMinecraftAddress(input string) (*ResolvedAddress, error) {
	// Se já tem porta explícita
	if host, portStr, err := net.SplitHostPort(input); err == nil {
		port, err := strconv.Atoi(portStr)
		if err != nil {
			return nil, err
		}

		return &ResolvedAddress{
			LogicalHost: host,
			Host:        host,
			Port:        uint16(port),
		}, nil
	}

	// Tentativa de SRV
	_, records, err := net.LookupSRV("minecraft", "tcp", input)
	if err == nil && len(records) > 0 {
		sort.Slice(records, func(i, j int) bool {
			return records[i].Priority < records[j].Priority
		})

		rec := records[0]

		return &ResolvedAddress{
			LogicalHost: input,
			Host:        strings.TrimSuffix(rec.Target, "."),
			Port:        rec.Port,
		}, nil
	}

	// Fallback (comportamento do launcher)
	return &ResolvedAddress{
		LogicalHost: input,
		Host:        input,
		Port:        25565,
	}, nil
}

func ResolveServerStatus(input string, ttl time.Duration) (*CachedResolution, error) {
	resolveMu.Lock()
	if entry, ok := resolveCache[input]; ok && time.Now().Before(entry.Expires) {
		resolveMu.Unlock()
		return entry, nil
	}
	resolveMu.Unlock()

	// resolve SRV / fallback
	addr, err := ResolveMinecraftAddress(input)
	if err != nil {
		return nil, err
	}

	ips, err := net.LookupIP(addr.Host)
	if err != nil {
		return nil, err
	}

	// ordenar IPv4 primeiro
	var v4, v6 []net.IP
	for _, ip := range ips {
		if ip.To4() != nil {
			v4 = append(v4, ip)
		} else {
			v6 = append(v6, ip)
		}
	}

	entry := &CachedResolution{
		Resolved: addr,
		IPs:      append(v4, v6...),
		Expires:  time.Now().Add(ttl),
	}

	resolveMu.Lock()
	resolveCache[input] = entry
	resolveMu.Unlock()

	return entry, nil
}

// ===== Utilidades de protocolo =====

func writeVarInt(buf *bytes.Buffer, value int) {
	for {
		if (value & ^0x7F) == 0 {
			buf.WriteByte(byte(value))
			return
		}
		buf.WriteByte(byte(value&0x7F | 0x80))
		value >>= 7
	}
}

func readVarInt(r *bufio.Reader) (int, error) {
	var num int
	var shift uint

	for {
		b, err := r.ReadByte()
		if err != nil {
			return 0, err
		}

		num |= int(b&0x7F) << shift
		if b&0x80 == 0 {
			break
		}
		shift += 7
	}

	return num, nil
}

// ===== Ping Minecraft (q vai ser usado no bot) =====

func Ping(res *CachedResolution, timeout time.Duration) (*StatusSlim, error) {
	var conn net.Conn
	var err error

	for _, ip := range res.IPs {
		target := net.JoinHostPort(ip.String(), strconv.Itoa(int(res.Resolved.Port)))
		conn, err = net.DialTimeout("tcp", target, timeout)
		if err == nil {
			break
		}
	}
	if conn == nil {
		return nil, fmt.Errorf("nenhum IP conseguiu conectar")
	}
	defer conn.Close()
	_ = conn.SetDeadline(time.Now().Add(timeout))

	writer := bufio.NewWriter(conn)
	reader := bufio.NewReader(conn)

	handshake := bufferPool.Get().(*bytes.Buffer)
	packet := bufferPool.Get().(*bytes.Buffer)
	handshake.Reset()
	packet.Reset()
	defer bufferPool.Put(handshake)
	defer bufferPool.Put(packet)

	writeVarInt(handshake, 0x00)
	writeVarInt(handshake, 763)

	writeVarInt(handshake, len(res.Resolved.LogicalHost))
	handshake.WriteString(res.Resolved.LogicalHost)

	_ = binary.Write(handshake, binary.BigEndian, res.Resolved.Port)
	writeVarInt(handshake, 1)

	writeVarInt(packet, handshake.Len())
	packet.Write(handshake.Bytes())

	if _, err := writer.Write(packet.Bytes()); err != nil {
		return nil, err
	}
	writer.Flush()

	writer.Write([]byte{0x01, 0x00})
	writer.Flush()

	if _, err = readVarInt(reader); err != nil {
		return nil, err
	}
	if _, err = readVarInt(reader); err != nil {
		return nil, err
	}

	jsonLen, err := readVarInt(reader)
	if err != nil {
		return nil, err
	}

	jsonData := make([]byte, jsonLen)
	if _, err = io.ReadFull(reader, jsonData); err != nil {
		return nil, err
	}

	var status StatusSlim
	if err := json.Unmarshal(jsonData, &status); err != nil {
		return nil, err
	}

	return &status, nil
}
