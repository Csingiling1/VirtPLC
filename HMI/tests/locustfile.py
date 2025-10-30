"""
HMI Performance Tests using Locust
Tests the performance and load handling capabilities of the HMI service
"""

from locust import HttpUser, task, between
import json
import random


class HMIUser(HttpUser):
    """Simulates HMI user interactions for performance testing"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Setup before starting the test"""
        self.auth_token = None
        # In a real scenario, you would authenticate here
        # For now, we'll assume the HMI is accessible without auth

    @task(3)  # Higher weight - more frequent
    def get_status_ping(self):
        """Test the health check endpoint"""
        self.client.get("/StatusPing")

    @task(2)
    def get_system_status(self):
        """Test system status endpoint"""
        self.client.get("/system/status")

    @task(2)
    def get_tag_values(self):
        """Test tag value retrieval"""
        # Simulate requesting different tag values
        tag_names = [
            "sensor.temperature",
            "sensor.pressure",
            "sensor.flow_rate",
            "actuator.valve_position",
            "actuator.pump_speed"
        ]
        tag_name = random.choice(tag_names)
        self.client.get(f"/api/tags/{tag_name}")

    @task(1)
    def get_dashboard_data(self):
        """Test dashboard data retrieval"""
        self.client.get("/api/dashboard/overview")

    @task(1)
    def get_historical_data(self):
        """Test historical data retrieval"""
        # Simulate requesting historical data for different time ranges
        params = {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-02T00:00:00Z",
            "tags": "sensor.temperature,sensor.pressure"
        }
        self.client.get("/api/historical", params=params)

    @task(1)
    def websocket_simulation(self):
        """Simulate WebSocket connection establishment"""
        # Locust doesn't directly support WebSocket testing well,
        # but we can test the WebSocket upgrade endpoint
        headers = {
            "Upgrade": "websocket",
            "Connection": "Upgrade",
            "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
            "Sec-WebSocket-Version": "13"
        }
        self.client.get("/websocket", headers=headers)

    @task(1)
    def post_tag_write(self):
        """Test tag write operations"""
        data = {
            "tag_name": "actuator.valve_position",
            "value": random.uniform(0, 100),
            "quality": "GOOD"
        }
        self.client.post("/api/tags/write",
                        json=data,
                        headers={"Content-Type": "application/json"})


class HeavyLoadUser(HMIUser):
    """User class for heavy load testing scenarios"""

    wait_time = between(0.1, 0.5)  # Much faster interactions

    @task(5)
    def rapid_status_checks(self):
        """Rapid status ping checks"""
        self.client.get("/StatusPing")

    @task(3)
    def rapid_tag_reads(self):
        """Rapid tag value reads"""
        tag_names = [f"sensor.temp_{i}" for i in range(10)]
        tag_name = random.choice(tag_names)
        self.client.get(f"/api/tags/{tag_name}")


class DataIntensiveUser(HMIUser):
    """User class for data-intensive operations"""

    wait_time = between(2, 5)

    @task
    def large_historical_query(self):
        """Large historical data queries"""
        params = {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-07T00:00:00Z",  # Week of data
            "tags": ",".join([f"sensor.data_{i}" for i in range(20)]),  # Many tags
            "aggregation": "1h"  # Hourly aggregation
        }
        self.client.get("/api/historical", params=params)

    @task
    def bulk_tag_read(self):
        """Bulk tag reading operations"""
        data = {
            "tag_names": [f"sensor.bulk_{i}" for i in range(50)]
        }
        self.client.post("/api/tags/bulk-read",
                        json=data,
                        headers={"Content-Type": "application/json"})