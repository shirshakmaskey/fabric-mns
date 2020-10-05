package chaincode

import (
	"encoding/json"
	"fmt"
	"log"
	"net"
	"os"
	"strconv"
	"strings"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// SocketClient connects to python-memcached server
func SocketClient(ip string, port int, message []byte) []byte {
	addr := strings.Join([]string{ip, strconv.Itoa(port)}, ":")
	conn, err := net.Dial("tcp", addr)

	if err != nil {
		log.Fatalln(err)
		os.Exit(1)
	}

	conn.Write(message)
	log.Printf("Send: %s", message)

	buff := make([]byte, 1024)
	n, _ := conn.Read(buff)
	return buff[:n]

}

// SmartContract provides functions for managing an Asset
type SmartContract struct {
	contractapi.Contract
}

// NodeTableData structure for python-memcached server.
type NodeTableData struct {
	Test string
}

// Asset describes basic details of what makes up a simple asset
type Asset struct {
	TripID        string `json:"TripID"`
	TimeStep      string `json:"TimeStep"`
	TimeStamp     string `json:"TimeStamp"`
	Speed         string `json:"Speed"`
	Acceleration  string `json:"Acceleration"`
	Heading       string `json:"Heading"`
	HeadingChange string `json:"HeadingChange"`
	Latitude      string `json:"Latitude"`
	Longitude     string `json:"Longitude"`
	Annotation    string `json:"Annotation"`
	SegmentType   string `json:"SegmentType"`
}

// InitLedger adds a base set of assets to the ledger
func (s *SmartContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
	assets := []Asset{
		{TripID: "T-1", TimeStep: "659", TimeStamp: "Wed Jul 24 15:58:22 EDT 2013", Speed: "29", Acceleration: "0", Heading: "84", HeadingChange: "0", Latitude: "39.980572", Longitude: "-82.953895", Annotation: "NULL", SegmentType: "NULL"},
		{TripID: "T-2", TimeStep: "593", TimeStamp: "Wed Feb 29 18:17:21 EST 2012", Speed: "50", Acceleration: "0.56", Heading: "312", HeadingChange: "0", Latitude: "39.979262", Longitude: "-83.117595", Annotation: "NULL", SegmentType: "NULL"},
		{TripID: "T-3", TimeStep: "405", TimeStamp: "Mon Apr 16 15:22:24 EDT 2012", Speed: "63", Acceleration: "0.56", Heading: "18", HeadingChange: "0", Latitude: "39.989355", Longitude: "-82.937508", Annotation: "NULL", SegmentType: "NULL"},
		{TripID: "T-4", TimeStep: "539", TimeStamp: "Thu Aug 16 15:17:25 EDT 2012", Speed: "48", Acceleration: "0", Heading: "276", HeadingChange: "0", Latitude: "39.976715", Longitude: "-83.112657", Annotation: "NULL", SegmentType: "NULL"},
		{TripID: "T-5", TimeStep: "371", TimeStamp: "Thu Jul 12 15:13:32 EDT 2012", Speed: "0", Acceleration: "0", Heading: "246", HeadingChange: "0", Latitude: "39.967263", Longitude: "-83.026538", Annotation: "NULL", SegmentType: "NULL"},
	}

	for _, asset := range assets {
		assetJSON, err := json.Marshal(asset)
		if err != nil {
			return err
		}

		err = ctx.GetStub().PutState(asset.TripID, assetJSON)
		if err != nil {
			return fmt.Errorf("failed to put to world state. %v", err)
		}
	}

	return nil
}

// ReadAsset returns the asset stored in the world state with given id.
func (s *SmartContract) ReadAsset(ctx contractapi.TransactionContextInterface, id string) (*Asset, error) {
	assetJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if assetJSON == nil {
		return nil, fmt.Errorf("the asset %s does not exist", id)
	}

	var asset Asset
	err = json.Unmarshal(assetJSON, &asset)
	if err != nil {
		return nil, err
	}

	return &asset, nil
}

// UpdateAsset updates an existing asset in the world state with provided parameters.
func (s *SmartContract) UpdateAsset(ctx contractapi.TransactionContextInterface, tripID string, timeStep string, timeStamp string, speed string, acceleration string, heading string, headingChange string, latitude string, longitude string, annotation string, segmentType string) error {
	// overwriting original asset with new asset
	asset := Asset{
		TripID:        tripID,
		TimeStep:      timeStep,
		TimeStamp:     timeStamp,
		Speed:         speed,
		Acceleration:  acceleration,
		Heading:       heading,
		HeadingChange: headingChange,
		Latitude:      latitude,
		Longitude:     longitude,
		Annotation:    annotation,
		SegmentType:   segmentType,
	}
	assetJSON, err := json.Marshal(asset)
	if err != nil {
		return err
	}
	testing := NodeTableData{"hello world"}
	mlJSONByte, err := json.Marshal(testing)
	if err != nil {
	}
	var ml NodeTableData
	byteOutput := SocketClient("reputationServer", 5555, mlJSONByte)
	if err = json.Unmarshal(byteOutput, &ml); err != nil {
	}
	// a := ml.test
	// fmt.Println(a)
	return ctx.GetStub().PutState(tripID, assetJSON)
}

// AssetExists returns true when asset with given ID exists in world state
func (s *SmartContract) AssetExists(ctx contractapi.TransactionContextInterface, id string) (bool, error) {
	assetJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}

	return assetJSON != nil, nil
}

// GetAllAssets returns all assets found in world state
func (s *SmartContract) GetAllAssets(ctx contractapi.TransactionContextInterface) ([]*Asset, error) {
	// range query with empty string for startKey and endKey does an
	// open-ended query of all assets in the chaincode namespace.
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var assets []*Asset
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var asset Asset
		err = json.Unmarshal(queryResponse.Value, &asset)
		if err != nil {
			return nil, err
		}
		assets = append(assets, &asset)
	}

	return assets, nil
}
