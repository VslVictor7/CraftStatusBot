package log

import (
	"fmt"
	"time"
)

var brLocation *time.Location

func init() {
	loc, err := time.LoadLocation("America/Sao_Paulo")
	if err != nil {
		brLocation = time.Local
		return
	}
	brLocation = loc
}

func LogInfo(msg string) {
	fmt.Println(
		time.Now().In(brLocation).Format("2006/01/02 15:04:05"),
		"[INFO]",
		msg,
	)
}

func LogOk(msg string) {
	fmt.Println(
		time.Now().In(brLocation).Format("2006/01/02 15:04:05"),
		"[OK]",
		msg,
	)
}

func LogError(msg string, err error) {
	fmt.Println(
		time.Now().In(brLocation).Format("2006/01/02 15:04:05"),
		"[ERROR]",
		msg,
		"-",
		err,
	)
}
