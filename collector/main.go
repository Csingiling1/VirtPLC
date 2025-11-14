package main

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/gopcua/opcua"
	"github.com/gopcua/opcua/ua"
	_ "github.com/lib/pq"
)

var lastDebugLog time.Time

type SensorData struct {
	Timestamp    time.Time
	DeviceID     string
	Motor1Speed  *float64
	Motor1Temp   *float64
	Motor1Run    *bool
	Motor1Fault  *bool
	Motor2Speed  *float64
	Motor2Temp   *float64
	Motor2Run    *bool
	Motor2Fault  *bool
	Conveyor1Speed *float64
	Conveyor1Run   *bool
	Sensor1Value   *float64
	Sensor2Value   *bool
	SystemStatus   string
}

func main() {
	// Database configuration
	dbHost := getEnv("TIMESCALE_HOST", "timescale")
	dbPort := getEnv("TIMESCALE_PORT", "5432")
	dbUser := getEnv("TIMESCALE_USER", "virtplc")
	dbPassword := getEnv("TIMESCALE_PASSWORD", "changeme")
	dbName := getEnv("TIMESCALE_DB", "virtplc_ts")

	// OPC-UA configuration
	opcuaEndpoint := getEnv("OPCUA_ENDPOINT", "opc.tcp://simulator:4840/virtplc/")
	collectionInterval := getEnv("COLLECTION_INTERVAL", "1000") // milliseconds

	intervalMs, err := time.ParseDuration(collectionInterval + "ms")
	if err != nil {
		log.Fatalf("Invalid collection interval: %v", err)
	}

	log.Printf("Starting VirtPLC Collector")
	log.Printf("TimescaleDB: %s:%s/%s", dbHost, dbPort, dbName)
	log.Printf("OPC-UA Endpoint: %s", opcuaEndpoint)
	log.Printf("Collection Interval: %v", intervalMs)

	// Connect to database
	db, err := connectDatabase(dbHost, dbPort, dbUser, dbPassword, dbName)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Main collection loop
	ticker := time.NewTicker(intervalMs)
	defer ticker.Stop()

	for range ticker.C {
		if err := collectAndStore(opcuaEndpoint, db); err != nil {
			log.Printf("Collection failed: %v", err)
		}
	}
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

func getNamespaceIndex(ctx context.Context, c *opcua.Client, uri string) (uint16, error) {
	// The namespace array is at node ID ns=0;i=2255
	nodeID := ua.NewNumericNodeID(0, 2255)
	node := c.Node(nodeID)
	v, err := node.Value(ctx)
	if err != nil {
		return 0, err
	}
	ns, ok := v.Value().([]string)
	if !ok {
		return 0, fmt.Errorf("namespace array is not a string array")
	}
	for i, u := range ns {
		if u == uri {
			return uint16(i), nil
		}
	}
	return 0, fmt.Errorf("namespace URI %s not found", uri)
}

func collectAndStore(opcuaEndpoint string, db *sql.DB) error {
	ctx := context.Background()
	c, err := opcua.NewClient(opcuaEndpoint, opcua.SecurityMode(ua.MessageSecurityModeNone))
	if err != nil {
		return fmt.Errorf("failed to create OPC-UA client: %w", err)
	}

	if err := c.Connect(ctx); err != nil {
		return fmt.Errorf("failed to connect to OPC-UA server: %w", err)
	}
	defer c.Close(ctx)

	// Get namespace index for our URI
	nsURI := "http://virtplc.simulator"
	nsIdx, err := getNamespaceIndex(ctx, c, nsURI)
	if err != nil {
		return fmt.Errorf("failed to get namespace index: %w", err)
	}
	log.Printf("Using namespace index %d for URI %s", nsIdx, nsURI)

	// Small delay to ensure server is ready
	time.Sleep(2 * time.Second)

	// Read sensor values
	data, err := readOPCUASensors(ctx, c, nsIdx)
	if err != nil {
		return fmt.Errorf("failed to read OPC-UA sensors: %w", err)
	}

	// Store in database
	if err := insertSensorData(db, data); err != nil {
		return fmt.Errorf("failed to insert sensor data: %w", err)
	}

	log.Printf("Successfully collected and stored sensor data")
	return nil
}

func readOPCUASensors(ctx context.Context, c *opcua.Client, nsIdx uint16) (*SensorData, error) {
	data := &SensorData{
		Timestamp:    time.Now(),
		DeviceID:     "virtplc-simulator",
		SystemStatus: "Running",
	}

	// Define node IDs for sensors (adjust based on your OPC-UA server setup)
	nodeIDs := map[string]string{
		"Motor1_Speed":  fmt.Sprintf("ns=%d;s=Motor1.Speed", nsIdx),
		"Motor1_Temp":   fmt.Sprintf("ns=%d;s=Motor1.Temperature", nsIdx),
		"Motor1_Run":    fmt.Sprintf("ns=%d;s=Motor1.Running", nsIdx),
		"Motor1_Fault":  fmt.Sprintf("ns=%d;s=Motor1.Fault", nsIdx),
		"Motor2_Speed":  fmt.Sprintf("ns=%d;s=Motor2.Speed", nsIdx),
		"Motor2_Temp":   fmt.Sprintf("ns=%d;s=Motor2.Temperature", nsIdx),
		"Motor2_Run":    fmt.Sprintf("ns=%d;s=Motor2.Running", nsIdx),
		"Motor2_Fault":  fmt.Sprintf("ns=%d;s=Motor2.Fault", nsIdx),
		"Conveyor1_Speed": fmt.Sprintf("ns=%d;s=Conveyor1.Speed", nsIdx),
		"Conveyor1_Run":   fmt.Sprintf("ns=%d;s=Conveyor1.Running", nsIdx),
		"Sensor1_Value":   fmt.Sprintf("ns=%d;s=Sensor1.Value", nsIdx),
		"Sensor2_Value":   fmt.Sprintf("ns=%d;s=Sensor2.Value", nsIdx),
	}

	// Read all values in a single request for efficiency
	req := &ua.ReadRequest{
		MaxAge: 2000,
		NodesToRead: []*ua.ReadValueID{},
	}

	for _, nodeID := range nodeIDs {
		nodeIDParsed, err := ua.ParseNodeID(nodeID)
		if err != nil {
			log.Printf("Failed to parse node ID %s: %v", nodeID, err)
			continue
		}
		req.NodesToRead = append(req.NodesToRead, &ua.ReadValueID{
			NodeID: nodeIDParsed,
		})
	}

	resp, err := c.Read(ctx, req)
	if err != nil {
		return nil, err
	}

	if resp.Results[0].Status != ua.StatusOK {
		log.Printf("OPC-UA read failed for some nodes, continuing with available data")
	}

	// Parse results
	for i, result := range resp.Results {
		if result.Status != ua.StatusOK {
			log.Printf("OPC-UA read failed for node %d: status=%v", i, result.Status)
			continue
		}
		log.Printf("OPC-UA read success for node %d: value=%v", i, result.Value.Value())

		var nodeName string
		for name, id := range nodeIDs {
			if i < len(req.NodesToRead) {
				expectedNodeID, _ := ua.ParseNodeID(id)
				if req.NodesToRead[i].NodeID.String() == expectedNodeID.String() {
					nodeName = name
					break
				}
			}
		}

		switch nodeName {
		case "Motor1_Speed":
			if val, ok := result.Value.Value().(float64); ok {
				data.Motor1Speed = &val
			}
		case "Motor1_Temp":
			if val, ok := result.Value.Value().(float64); ok {
				data.Motor1Temp = &val
			}
		case "Motor1_Run":
			if val, ok := result.Value.Value().(bool); ok {
				data.Motor1Run = &val
			}
		case "Motor1_Fault":
			if val, ok := result.Value.Value().(bool); ok {
				data.Motor1Fault = &val
			}
		case "Motor2_Speed":
			if val, ok := result.Value.Value().(float64); ok {
				data.Motor2Speed = &val
			}
		case "Motor2_Temp":
			if val, ok := result.Value.Value().(float64); ok {
				data.Motor2Temp = &val
			}
		case "Motor2_Run":
			if val, ok := result.Value.Value().(bool); ok {
				data.Motor2Run = &val
			}
		case "Motor2_Fault":
			if val, ok := result.Value.Value().(bool); ok {
				data.Motor2Fault = &val
			}
		case "Conveyor1_Speed":
			if val, ok := result.Value.Value().(float64); ok {
				data.Conveyor1Speed = &val
			}
		case "Conveyor1_Run":
			if val, ok := result.Value.Value().(bool); ok {
				data.Conveyor1Run = &val
			}
		case "Sensor1_Value":
			if val, ok := result.Value.Value().(float64); ok {
				data.Sensor1Value = &val
			}
		case "Sensor2_Value":
			if val, ok := result.Value.Value().(bool); ok {
				data.Sensor2Value = &val
			}
		}
	}

	// Debug logging every 3 seconds
	if time.Since(lastDebugLog) > 3*time.Second {
		log.Printf("DEBUG: Collected sensor data - Motor1Speed: %v, Motor1Temp: %v, Motor1Run: %v, Motor1Fault: %v, Motor2Speed: %v, Motor2Temp: %v, Motor2Run: %v, Motor2Fault: %v, Conveyor1Speed: %v, Conveyor1Run: %v, Sensor1Value: %v, Sensor2Value: %v",
			derefFloat64(data.Motor1Speed), derefFloat64(data.Motor1Temp), derefBool(data.Motor1Run), derefBool(data.Motor1Fault),
			derefFloat64(data.Motor2Speed), derefFloat64(data.Motor2Temp), derefBool(data.Motor2Run), derefBool(data.Motor2Fault),
			derefFloat64(data.Conveyor1Speed), derefBool(data.Conveyor1Run), derefFloat64(data.Sensor1Value), derefBool(data.Sensor2Value))
		lastDebugLog = time.Now()
	}

	return data, nil
}

func insertSensorData(db *sql.DB, data *SensorData) error {
	query := `
		INSERT INTO sensor_data (
			timestamp, device_id, motor1_speed, motor1_temp, motor1_run, motor1_fault,
			motor2_speed, motor2_temp, motor2_run, motor2_fault, conveyor1_speed,
			conveyor1_run, sensor1_value, sensor2_value, system_status
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
	`

	_, err := db.Exec(query,
		data.Timestamp, data.DeviceID, data.Motor1Speed, data.Motor1Temp, data.Motor1Run, data.Motor1Fault,
		data.Motor2Speed, data.Motor2Temp, data.Motor2Run, data.Motor2Fault, data.Conveyor1Speed,
		data.Conveyor1Run, data.Sensor1Value, data.Sensor2Value, data.SystemStatus,
	)

	return err
}

func derefFloat64(ptr *float64) interface{} {
	if ptr == nil {
		return nil
	}
	return *ptr
}

func derefBool(ptr *bool) interface{} {
	if ptr == nil {
		return nil
	}
	return *ptr
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}