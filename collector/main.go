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

type PLCData struct {
	Timestamp float64                `json:"timestamp"`
	Tenants   map[string]interface{} `json:"tenants"`
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

	// Subscribe to PLC data
	client.Subscribe("plc/data", 0, func(client MQTT.Client, msg MQTT.Message) {
		var data PLCData
		if err := json.Unmarshal(msg.Payload(), &data); err != nil {
			log.Printf("Failed to parse MQTT message: %v", err)
			return
		}

		// Process and store data
		if err := processAndStore(db, data); err != nil {
			log.Printf("Failed to process and store data: %v", err)
		} else {
			log.Printf("Successfully processed and stored PLC data")
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

func processAndStore(db *sql.DB, data PLCData) error {
	timestamp := time.Unix(int64(data.Timestamp), 0)

	// Example: Insert into a table (adjust based on your schema)
	query := `
		INSERT INTO plc_data (timestamp, data)
		VALUES ($1, $2)
	`

	jsonData, err := json.Marshal(data.Tenants)
	if err != nil {
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