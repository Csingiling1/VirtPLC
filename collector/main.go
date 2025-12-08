package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"time"

	MQTT "github.com/eclipse/paho.mqtt.golang"
	_ "github.com/lib/pq"
)

type DeviceData struct {
	DeviceID  string                 `json:"device_id"`
	Type      string                 `json:"type"`
	Timestamp float64                `json:"timestamp"`
	Data      map[string]interface{} `json:"data"`
	Metadata  map[string]interface{} `json:"metadata"`
}

func main() {
	// Database configuration
	dbHost := getEnv("TIMESCALE_HOST", "timescale")
	dbPort := getEnv("TIMESCALE_PORT", "5432")
	dbUser := getEnv("TIMESCALE_USER", "virtplc")
	dbPassword := getEnv("TIMESCALE_PASSWORD", "changeme")
	dbName := getEnv("TIMESCALE_DB", "virtplc_ts")

	// MQTT configuration
	mqttBroker := getEnv("MQTT_BROKER", "mqtt")
	mqttPort := getEnv("MQTT_PORT", "1883")

	log.Printf("Starting VirtPLC Collector")
	log.Printf("TimescaleDB: %s:%s/%s", dbHost, dbPort, dbName)
	log.Printf("MQTT Broker: %s:%s", mqttBroker, mqttPort)

	// Connect to database
	db, err := connectDatabase(dbHost, dbPort, dbUser, dbPassword, dbName)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// MQTT Client
	opts := MQTT.NewClientOptions().AddBroker(fmt.Sprintf("tcp://%s:%s", mqttBroker, mqttPort))
	client := MQTT.NewClient(opts)
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		log.Fatalf("Failed to connect to MQTT broker: %v", token.Error())
	}
	defer client.Disconnect(250)

	log.Printf("Connected to MQTT broker")

	// Subscribe to Collector data (from Node-RED)
	client.Subscribe("collector/ingest", 0, func(client MQTT.Client, msg MQTT.Message) {
		var data DeviceData
		if err := json.Unmarshal(msg.Payload(), &data); err != nil {
			log.Printf("Failed to parse MQTT message: %v", err)
			return
		}

		// Process and store data
		if err := processAndStore(db, data); err != nil {
			log.Printf("Failed to process and store data: %v", err)
		} else {
			log.Printf("Successfully processed and stored device data: %s", data.DeviceID)
		}
	})

	// Keep running
	select {}
}

func connectDatabase(host, port, user, password, dbname string) (*sql.DB, error) {
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, err
	}

	if err := db.Ping(); err != nil {
		return nil, err
	}

	log.Printf("Connected to TimescaleDB")
	return db, nil
}

func processAndStore(db *sql.DB, data DeviceData) error {
	timestamp := time.Unix(int64(data.Timestamp), 0)

	// Example: Insert into a table (adjust based on your schema)
	query := `
		INSERT INTO plc_data (timestamp, device_id, type, data, metadata)
		VALUES ($1, $2, $3, $4, $5)
	`

	jsonData, err := json.Marshal(data.Data)
	if err != nil {
		return err
	}
	
	jsonMetadata, err := json.Marshal(data.Metadata)
	if err != nil {
		return err
	}

	_, err = db.Exec(query, timestamp, data.DeviceID, data.Type, jsonData, jsonMetadata)
	return err
}
}
		return err
	}

	_, err = db.Exec(query, timestamp, string(jsonData))
	return err
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}