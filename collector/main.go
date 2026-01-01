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
	DeviceID       string                 `json:"device_id"`
	Type           string                 `json:"type"`
	Timestamp      float64                `json:"timestamp"`
	Data           map[string]interface{} `json:"data"`
	Metadata       map[string]interface{} `json:"metadata"`
	ProcessedAt    string                 `json:"processed_at,omitempty"`
	NodeRedVersion string                 `json:"node_red_version,omitempty"`
	TopicOriginal  string                 `json:"topic_original,omitempty"`
	DataQuality    map[string]interface{} `json:"data_quality,omitempty"`
	Category       string                 `json:"category,omitempty"`
	Priority       string                 `json:"priority,omitempty"`
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
	opts.SetClientID("virtplc-collector")
	opts.SetCleanSession(true)
	opts.SetAutoReconnect(true)
	
	mqttUsername := getEnv("MQTT_USERNAME", "")
	mqttPassword := getEnv("MQTT_PASSWORD", "")
	if mqttUsername != "" {
		log.Printf("Using MQTT authentication with username: %s", mqttUsername)
		opts.SetUsername(mqttUsername)
		opts.SetPassword(mqttPassword)
	} else {
		log.Printf("WARNING: No MQTT credentials provided")
	}
	
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

	// Enrich metadata with Node-RED processing information
	enrichedMetadata := make(map[string]interface{})
	for k, v := range data.Metadata {
		enrichedMetadata[k] = v
	}
	
	// Add Node-RED enrichment fields to metadata
	if data.ProcessedAt != "" {
		enrichedMetadata["processed_at"] = data.ProcessedAt
	}
	if data.NodeRedVersion != "" {
		enrichedMetadata["node_red_version"] = data.NodeRedVersion
	}
	if data.TopicOriginal != "" {
		enrichedMetadata["topic_original"] = data.TopicOriginal
	}
	if data.DataQuality != nil {
		enrichedMetadata["data_quality"] = data.DataQuality
	}
	if data.Category != "" {
		enrichedMetadata["category"] = data.Category
	}
	if data.Priority != "" {
		enrichedMetadata["priority"] = data.Priority
	}

	// Extract values for separate columns based on device type and data content
	var rpm, positionX, positionY *float64
	var isOn, inOperation *bool

	// Handle UNREAL device data
	if data.Type == "UNREAL" {
		// Extract rpm for conveyor devices
		if rpmVal, ok := data.Data["rpm"].(float64); ok {
			rpm = &rpmVal
		}
		
		// Extract position for placer devices
		if posXVal, ok := data.Data["posX"].(float64); ok {
			positionX = &posXVal
		}
		if posYVal, ok := data.Data["posY"].(float64); ok {
			positionY = &posYVal
		}
		
		// Extract boolean states
		if isOnVal, ok := data.Data["is_on"].(bool); ok {
			isOn = &isOnVal
		}
		if isReadyVal, ok := data.Data["is_ready"].(bool); ok {
			inOperation = &isReadyVal  // Map is_ready to in_operation column
		}
	} else if data.Type == "sensor" {
		// Handle sensor data - extract value from signal_config
		if signalConfig, ok := data.Data["signal_config"].(map[string]interface{}); ok {
			if value, ok := signalConfig["value"].(float64); ok {
				rpm = &value
			}
		}
	} else if data.Type == "plc" {
		// Handle PLC data
		if x, ok := data.Data["x_position"].(float64); ok {
			positionX = &x
		}
		if y, ok := data.Data["y_position"].(float64); ok {
			positionY = &y
		}
		if active, ok := data.Data["is_active"].(bool); ok {
			isOn = &active
		}
	}

	// Insert into database
	query := `
		INSERT INTO plc_data (timestamp, device_id, type, data, metadata, rpm, position_x, position_y, is_on, in_operation)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
	`

	jsonData, err := json.Marshal(data.Data)
	if err != nil {
		return err
	}
	
	jsonMetadata, err := json.Marshal(enrichedMetadata)
	if err != nil {
		return err
	}

	_, err = db.Exec(query, timestamp, data.DeviceID, data.Type, jsonData, jsonMetadata, rpm, positionX, positionY, isOn, inOperation)
	return err
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}