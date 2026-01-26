/*
VirtPLC Collector Service

This service subscribes to MQTT topics and persists enriched device data to TimescaleDB.
It handles both real-time PLC data and simulated factory data, providing high-performance
time-series data ingestion with automatic batching and error handling.

Architecture:
  MQTT Broker (factory/processed) → Collector Service → TimescaleDB

Supported Data Types:
  - UNREAL: Unreal Engine factory simulation data (conveyors, placers)
  - sensor: PLC sensor data with signal configurations

Environment Variables:
  TIMESCALE_HOST     - TimescaleDB hostname (default: timescale)
  TIMESCALE_PORT     - TimescaleDB port (default: 5432)
  TIMESCALE_USER     - Database username (default: virtplc)
  TIMESCALE_PASSWORD - Database password (default: changeme)
  TIMESCALE_DB       - Database name (default: virtplc_ts)
  MQTT_BROKER        - MQTT broker hostname (default: mqtt)
  MQTT_PORT          - MQTT broker port (default: 1883)
  MQTT_USERNAME      - MQTT username (optional)
  MQTT_PASSWORD      - MQTT password (optional)
*/
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

// DeviceData represents the enriched data structure received from Node-RED
// via MQTT. It contains device telemetry along with quality metrics and
// processing metadata added by the Node-RED enrichment pipeline.
type DeviceData struct {
	DeviceID       string                 `json:"device_id"`        // Unique device identifier
	Type           string                 `json:"type"`             // Device type (UNREAL or sensor)
	Timestamp      float64                `json:"timestamp"`        // Unix timestamp (seconds since epoch)
	Data           map[string]interface{} `json:"data"`             // Raw telemetry data (RPM, position, etc.)
	Metadata       map[string]interface{} `json:"metadata"`         // Additional device metadata
	ProcessedAt    string                 `json:"processed_at,omitempty"`    // Node-RED processing timestamp
	NodeRedVersion string                 `json:"node_red_version,omitempty"` // Node-RED version info
	TopicOriginal  string                 `json:"topic_original,omitempty"`   // Original MQTT topic
	DataQuality    map[string]interface{} `json:"data_quality,omitempty"`     // Quality validation results
	Category       string                 `json:"category,omitempty"`         // Data category
	Priority       string                 `json:"priority,omitempty"`         // Message priority
}

// main initializes the collector service, establishes connections to
// TimescaleDB and MQTT broker, and sets up message handlers.
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

	// Subscribe to enriched data from Node-RED
	// The collector/ingest topic receives data that has already been validated
	// and enriched by Node-RED, including quality metrics and metadata.
	client.Subscribe("collector/ingest", 0, func(client MQTT.Client, msg MQTT.Message) {
		log.Printf("DEBUG: Received MQTT message: %s", string(msg.Payload()))
		
		// Parse incoming JSON message
		var data DeviceData
		if err := json.Unmarshal(msg.Payload(), &data); err != nil {
			log.Printf("Failed to parse MQTT message: %v", err)
			return
		}
		log.Printf("DEBUG: Parsed device_id=%s type=%s timestamp=%f", data.DeviceID, data.Type, data.Timestamp)
		log.Printf("DEBUG: Data map: %+v", data.Data)

		// Process and persist to TimescaleDB
		if err := processAndStore(db, data); err != nil {
			log.Printf("Failed to process and store data: %v", err)
		} else {
			log.Printf("Successfully processed and stored device data: %s", data.DeviceID)
		}
	})

// connectDatabase establishes a connection to TimescaleDB using PostgreSQL driver.
// It verifies the connection with a ping before returning.
//
// Parameters:
//   - host: Database hostname
//   - port: Database port
//   - user: Database username
//   - password: Database password
//   - dbname: Database name
//
// Returns:
//   - *sql.DB: Database connection handle
//   - error: Connection error if any
func connectDatabase(host, port, user, password, dbname string) (*sql.DB, error) {
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, err
	}
// processAndStore extracts relevant fields from DeviceData and inserts them
// into TimescaleDB's plc_data hypertable. It handles different device types
// (UNREAL vs sensor) and extracts type-specific fields into dedicated columns.
//
// Data Mapping:
//   - UNREAL devices: RPM, position, and state fields extracted
//   - sensor devices: Signal value extracted from signal_config
//   - All types: Full data and metadata stored as JSONB
//
// Parameters:
//   - db: Database connection handle
//   - data: Enriched device data from Node-RED
//
// Returns:
//   - error: Database insertion error if any
func processAndStore(db *sql.DB, data DeviceData) error {
	timestamp := time.Unix(int64(data.Timestamp), 0)

	// Enrich metadata with Node-RED processing information
	// This preserves all enrichment data added by the Node-RED pipeline
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
// getEnv retrieves an environment variable with a fallback default value.
// This is used for configuration with sensible defaults for development.
//
// Parameters:
//   - key: Environment variable name
//   - defaultValue: Value to return if environment variable is not set
//
// Returns:
//   - string: Environment variable value or default
		}
	} else if data.Type == "sensor" {
		// Handle sensor data - extract value from signal_config and store in rpm column
		if signalConfig, ok := data.Data["signal_config"].(map[string]interface{}); ok {
			if value, ok := signalConfig["value"].(float64); ok {
				rpm = &value
			}
		}
	}

	// Insert into plc_data table  
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