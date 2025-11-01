package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"
)

type Sensor struct {
	ID        string  `json:"id"`
	Name      string  `json:"name"`
	Value     float64 `json:"value"`
	Unit      string  `json:"unit"`
	Timestamp int64   `json:"timestamp"`
}

type PLC struct {
	ID      string   `json:"id"`
	Name    string   `json:"name"`
	Sensors []Sensor `json:"sensors"`
}

type Factory struct {
	ID    string `json:"id"`
	Name  string `json:"name"`
	PLCs  []PLC  `json:"plcs"`
}

type Manufacturer struct {
	ID       string    `json:"id"`
	Name     string    `json:"name"`
	Factories []Factory `json:"factories"`
}

type Tenant struct {
	ID            string         `json:"id"`
	Name          string         `json:"name"`
	Manufacturers []Manufacturer `json:"manufacturers"`
}

type SimulatorResponse struct {
	Timestamp int64    `json:"timestamp"`
	Tenants   []Tenant `json:"tenants"`
}

type TelemetryReading struct {
	TenantID       string  `json:"tenantId"`
	ManufacturerID string  `json:"manufacturerId"`
	FactoryID      string  `json:"factoryId"`
	PLCID          string  `json:"plcId"`
	SensorID       string  `json:"sensorId"`
	Value          float64 `json:"value"`
	Unit           string  `json:"unit"`
	Timestamp      int64   `json:"timestamp"`
}

func main() {
	simulatorURL := getEnv("SIMULATOR_URL", "http://simulator:8080")
	backendHost := getEnv("BACKEND_HOST", "backend")
	backendPort := getEnv("BACKEND_REST_PORT", "8080")
	tenantID := getEnv("TENANT_ID", "demo-tenant")

	log.Printf("Starting VirtPLC Collector")
	log.Printf("Simulator URL: %s", simulatorURL)
	log.Printf("Backend REST: %s:%s", backendHost, backendPort)
	log.Printf("Tenant ID: %s", tenantID)

	// Main collection loop - collect every second
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		collectAndStream(simulatorURL, backendHost, backendPort)
	}
}

func collectAndStream(simulatorURL, backendHost, backendPort string) {
	data, err := fetchSimulatorData(simulatorURL)
	if err != nil {
		log.Printf("Failed to fetch simulator data: %v", err)
		return
	}

	log.Printf("Fetched %d tenants from simulator", len(data.Tenants))
	streamToBackend(data, backendHost, backendPort)
}

func fetchSimulatorData(url string) (*SimulatorResponse, error) {
	resp, err := http.Get(url + "/api/stream/latest")
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var data SimulatorResponse
	if err := json.Unmarshal(body, &data); err != nil {
		return nil, err
	}

	return &data, nil
}

func streamToBackend(data *SimulatorResponse, backendHost, backendPort string) {
	readings := flattenData(data)

	url := fmt.Sprintf("http://%s:%s/api/data/ingest", backendHost, backendPort)

	jsonData, err := json.Marshal(readings)
	if err != nil {
		log.Printf("Failed to marshal readings: %v", err)
		return
	}

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		log.Printf("Failed to stream data: %v", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		log.Printf("Successfully streamed %d readings to backend", len(readings))
	} else {
		log.Printf("Failed to stream data: HTTP %d", resp.StatusCode)
	}
}

func flattenData(data *SimulatorResponse) []TelemetryReading {
	var readings []TelemetryReading

	for _, tenant := range data.Tenants {
		for _, manufacturer := range tenant.Manufacturers {
			for _, factory := range manufacturer.Factories {
				for _, plc := range factory.PLCs {
					for _, sensor := range plc.Sensors {
						reading := TelemetryReading{
							TenantID:       tenant.ID,
							ManufacturerID: manufacturer.ID,
							FactoryID:      factory.ID,
							PLCID:          plc.ID,
							SensorID:       sensor.ID,
							Value:          sensor.Value,
							Unit:           sensor.Unit,
							Timestamp:      time.Now().UnixMilli(),
						}
						readings = append(readings, reading)
					}
				}
			}
		}
	}

	return readings
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}