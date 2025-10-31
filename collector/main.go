package main

import (
	"context"
	"encoding/json"
	"flag"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"

	pb "github.com/virtplc/collector/proto"
	"google.golang.org/grpc"
	"google.golang.org/protobuf/types/known/timestamppb"

	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// SimulatorData represents the hierarchical JSON structure from the simulator
type SimulatorData struct {
	Tenants []Tenant `json:"tenants"`
}

type Tenant struct {
	ID           string        `json:"id"`
	Name         string        `json:"name"`
	Manufacturers []Manufacturer `json:"manufacturers"`
}

type Manufacturer struct {
	ID      string   `json:"id"`
	Name    string   `json:"name"`
	Factories []Factory `json:"factories"`
}

type Factory struct {
	ID   string `json:"id"`
	Name string `json:"name"`
	PLCs []PLC  `json:"plcs"`
}

type PLC struct {
	ID      string   `json:"id"`
	Name    string   `json:"name"`
	Sensors []Sensor `json:"sensors"`
}

type Sensor struct {
	ID    string  `json:"id"`
	Name  string  `json:"name"`
	Value float64 `json:"value"`
	Unit  string  `json:"unit"`
}

var (
	backendHost = envOrDefault("BACKEND_GRPC_HOST", "backend")
	backendPort = envOrDefault("BACKEND_GRPC_PORT", "9090")
	tenantID    = envOrDefault("TENANT_ID", "tenant-demo")
	simURL      = envOrDefault("OPCUA_SIMULATOR_URL", "http://simulator:8080")
)

func envOrDefault(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}

func main() {
	metricsPort := flag.String("metrics-port", "9100", "metrics port")
	flag.Parse()

	go func() {
		http.Handle("/metrics", promhttp.Handler())
		log.Fatal(http.ListenAndServe(":"+*metricsPort, nil))
	}()

	conn, err := grpc.Dial(backendHost+":"+backendPort, grpc.WithInsecure(), grpc.WithBlock())
	if err != nil {
		log.Fatalf("failed to connect backend: %v", err)
	}
	defer conn.Close()
	client := pb.NewPlcStreamClient(conn)

	ctx, cancel := context.WithCancel(context.Background())
	stream, err := client.StreamReadings(ctx)
	if err != nil {
		log.Fatalf("error creating stream: %v", err)
	}

	// handle graceful shutdown
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	go func() {
		<-c
		log.Println("shutting down collector")
		cancel()
		stream.CloseSend()
		time.Sleep(500 * time.Millisecond)
		os.Exit(0)
	}()

	// Poll simulator HTTP endpoint and stream sensor values
	for {
		// Fetch latest data from simulator
		resp, err := http.Get(simURL + "/api/stream/latest")
		if err != nil {
			log.Printf("failed to fetch simulator data: %v", err)
			time.Sleep(1 * time.Second)
			continue
		}

		var simData SimulatorData
		if err := json.NewDecoder(resp.Body).Decode(&simData); err != nil {
			log.Printf("failed to decode simulator response: %v", err)
			resp.Body.Close()
			time.Sleep(1 * time.Second)
			continue
		}
		resp.Body.Close()

		// Stream sensor readings from hierarchical data
		for _, tenant := range simData.Tenants {
			for _, manufacturer := range tenant.Manufacturers {
				for _, factory := range manufacturer.Factories {
					for _, plc := range factory.PLCs {
						for _, sensor := range plc.Sensors {
							reading := &pb.PlcReading{
								TenantId:       tenant.ID,
								ManufacturerId: manufacturer.ID,
								FactoryId:      factory.ID,
								PlcId:          plc.ID,
								SensorId:       sensor.ID,
								Timestamp:      timestamppb.Now(),
								Value:          sensor.Value,
								Unit:           sensor.Unit,
								Metadata:       "{}",
							}

							if err := stream.Send(reading); err != nil {
								log.Printf("stream send error: %v -- attempt reconnect", err)
								// try reconnect logic
								time.Sleep(200 * time.Millisecond)
								conn, _ = grpc.Dial(backendHost+":"+backendPort, grpc.WithInsecure(), grpc.WithBlock())
								client = pb.NewPlcStreamClient(conn)
								stream, _ = client.StreamReadings(ctx)
								break
							}
						}
					}
				}
			}
		}

		time.Sleep(100 * time.Millisecond) // adjust for required sampling rate
	}
}
