package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net"
	"os"
	"os/exec"
)

// JSONMessageDecode needs a comment otherwise it throws error
type JSONMessageDecode struct {
	PeerNode string `json:"PeerNode"`
	Action   string `json:"Action"`
	Final    int    `json:"Final"`
}

// main function is the entry point for the go server
func main() {
	fmt.Println("Starting miner node selection server...")
	clientConenction, _ := net.Listen("tcp", "0.0.0.0:6666")
	for {
		connection, err := clientConenction.Accept()
		if err != nil {
			fmt.Println("encountered the following error, ", err)
		}
		go handleConnection(connection)
	}
}
func handleConnection(conn net.Conn) {
	buff := make([]byte, 1024)
	n, err := conn.Read(buff)
	defer conn.Close()
	if err != nil {
		log.Println("client left..")
		conn.Close()
		return
	}
	var message JSONMessageDecode
	if unmarshalErr := json.Unmarshal(buff[:n], &message); unmarshalErr != nil {
		fmt.Printf(unmarshalErr.Error())
	}
	x, err := json.Marshal(message)
	fmt.Println("the message is ", x)
	if err != nil {
		log.Println(err.Error())
	}
	fmt.Println("entering the function")
	runMyCodes(message.PeerNode, message.Action, message.Final)
}
func runMyCodes(arg1 string, arg2 string, arg3 int) {
	if _, err := os.Stat("./update"); os.IsNotExist(err) {
		log.Println("executing first command")
		makeArgs := []string{"./scripts/makeConfigFile.sh", arg1}
		cmd := exec.Command("/bin/bash", makeArgs...)
		_, err := cmd.Output()
		if err != nil {
			log.Println(err.Error())
		}
	}
	if arg3 == 1 {
		log.Println("executing third command")
		applyArgs := []string{"./scripts/applyUpdate.sh"}
		cmd := exec.Command("/bin/bash", applyArgs...)
		_, err := cmd.Output()
		if err != nil {
			log.Println(err.Error())
		}
	} else {
		log.Println("executing second command")
		signArgs := []string{"./scripts/signUpdate.sh"}
		cmd := exec.Command("/bin/bash", signArgs...)
		_, err := cmd.Output()
		if err != nil {
			log.Println(err.Error())
		}
	}
}
