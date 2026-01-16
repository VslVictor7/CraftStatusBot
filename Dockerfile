# ======================
# STAGE 1 — BUILD
# ======================
FROM golang:1.25.5-alpine AS app-builder

# Dependências mínimas
RUN apk add --no-cache ca-certificates

WORKDIR /app

COPY . .

RUN go mod download

ENV CGO_ENABLED=0
ENV GOOS=linux
ENV GOARCH=amd64

RUN go build -ldflags="-s -w" -o bot ./cmd/bot

# ======================
# STAGE 2 — PROD
# ======================
FROM scratch

COPY --from=app-builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
# the test program:
COPY --from=app-builder /app/bot /bot

ENTRYPOINT ["/bot"]