FROM golang:1.26.0-alpine AS app-builder

RUN apk add --no-cache ca-certificates tzdata

WORKDIR /app

COPY . .

RUN go mod download

ENV CGO_ENABLED=0
ENV GOOS=linux
ENV GOARCH=amd64

RUN go build -ldflags="-s -w" -o bot ./cmd/bot


FROM scratch

COPY --from=app-builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=app-builder /usr/share/zoneinfo/America/Sao_Paulo /usr/share/zoneinfo/America/Sao_Paulo
COPY --from=app-builder /usr/share/zoneinfo/UTC /usr/share/zoneinfo/UTC
COPY --from=app-builder /app/bot /bot

ENV TZ=America/Sao_Paulo

ENTRYPOINT ["/bot"]