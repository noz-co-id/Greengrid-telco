# Greengrid Telco - Example Queries & API Usage

## REST API Examples

### 1. Central Platform API

#### Health Check
```bash
curl http://localhost:8080/health | jq '.'
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-01T10:30:00.000Z",
  "services": {
    "influxdb": true,
    "mqtt": true
  }
}
```

#### Get All Sites (Geospatial)
```bash
curl http://localhost:8080/api/sites | jq '.'
```

**Response:**
```json
{
  "sites": [
    {
      "site_id": "CELL_SITE_001",
      "site_name": "Jakarta Cell Site 1",
      "site_type": "CELL",
      "longitude": 106.8456,
      "latitude": -6.2088,
      "address": "Jl. Sudirman, Jakarta",
      "province": "DKI Jakarta",
      "city": "Jakarta Selatan",
      "capacity_kw": 50.0,
      "status": null
    }
  ]
}
```

#### Get Real-time Metrics
```bash
# All gateways
curl http://localhost:8080/api/metrics/realtime | jq '.'

# Specific gateway
curl "http://localhost:8080/api/metrics/realtime?gateway_id=CELL_SITE_001" | jq '.'
```

#### Get Dashboard Summary
```bash
curl http://localhost:8080/api/dashboard/summary | jq '.'
```

**Response:**
```json
{
  "timestamp": "2026-01-01T10:30:00.000Z",
  "total_sites": 3,
  "active_gateways": 3,
  "total_power_kw": 650.0,
  "renewable_percentage": 35.2,
  "network_uptime": 99.8,
  "alerts": {
    "critical": 0,
    "warning": 2,
    "info": 5
  }
}
```

#### Get ESG Report
```bash
curl http://localhost:8080/api/esg/report | jq '.'
```

**Response:**
```json
{
  "report_date": "2026-01-01",
  "environmental": {
    "total_energy_consumption_mwh": 1250.5,
    "renewable_energy_percentage": 35.2,
    "carbon_emissions_tons": 450.3,
    "water_usage_m3": 12500,
    "waste_recycled_percentage": 68.5
  },
  "social": {
    "total_sites": 3,
    "communities_served": 15000,
    "jobs_created": 45,
    "local_procurement_percentage": 72.3
  },
  "governance": {
    "compliance_rate": 98.5,
    "safety_incidents": 2,
    "training_hours": 1250
  },
  "sdg_alignment": {
    "SDG7": "Affordable and Clean Energy - 35% renewable",
    "SDG9": "Industry, Innovation and Infrastructure - Network expansion",
    "SDG11": "Sustainable Cities - Urban connectivity",
    "SDG13": "Climate Action - Carbon reduction initiatives"
  }
}
```

### 2. Edge Gateway APIs

#### Cell Site
```bash
# Health check
curl http://localhost:8081/health | jq '.'

# Get current metrics
curl http://localhost:8081/api/metrics | jq '.metrics.energy_meter'

# Control genset
curl -X POST http://localhost:8081/api/control/genset/start | jq '.'
curl -X POST http://localhost:8081/api/control/genset/stop | jq '.'
```

**Metrics Response:**
```json
{
  "voltage_l1": 220.5,
  "voltage_l2": 220.2,
  "voltage_l3": 221.0,
  "current_l1": 15.2,
  "current_l2": 14.8,
  "current_l3": 15.5,
  "power_total_kw": 9.8,
  "energy_total_kwh": 1250.5,
  "power_factor": 0.95,
  "frequency": 50.0
}
```

#### Data Center
```bash
# Health check
curl http://localhost:8082/health | jq '.'

# Get current metrics
curl http://localhost:8082/api/metrics | jq '.'

# Get PUE metrics
curl http://localhost:8082/api/pue | jq '.'
```

**PUE Response:**
```json
{
  "pue": 1.45,
  "it_power_kw": 110.7,
  "total_facility_power_kw": 160.5,
  "cooling_power_kw": 24.7,
  "lighting_power_kw": 5.1,
  "other_power_kw": 20.0
}
```

#### Switch Room
```bash
# Health check
curl http://localhost:8083/health | jq '.'

# Get current metrics
curl http://localhost:8083/api/metrics | jq '.'

# Access HMI (in browser)
open http://localhost:8083
```

## MQTT Examples

### 1. Subscribe to All Topics
```bash
docker exec greengrid-mqtt mosquitto_sub \
  -h localhost \
  -u greengrid \
  -P greengrid123 \
  -t "greengrid/#" \
  -v
```

### 2. Subscribe to Specific Gateway
```bash
# Cell Site metrics
docker exec greengrid-mqtt mosquitto_sub \
  -h localhost \
  -u greengrid \
  -P greengrid123 \
  -t "greengrid/edge/CELL_SITE_001/metrics" \
  -v

# Data Center metrics
docker exec greengrid-mqtt mosquitto_sub \
  -h localhost \
  -u greengrid \
  -P greengrid123 \
  -t "greengrid/edge/DC_SITE_001/metrics" \
  -v

# Switch Room metrics
docker exec greengrid-mqtt mosquitto_sub \
  -h localhost \
  -u greengrid \
  -P greengrid123 \
  -t "greengrid/edge/SR_SITE_001/metrics" \
  -v
```

### 3. Subscribe to Status Updates
```bash
docker exec greengrid-mqtt mosquitto_sub \
  -h localhost \
  -u greengrid \
  -P greengrid123 \
  -t "greengrid/edge/+/status" \
  -v
```

### 4. Subscribe to Alerts
```bash
docker exec greengrid-mqtt mosquitto_sub \
  -h localhost \
  -u greengrid \
  -P greengrid123 \
  -t "greengrid/edge/+/alerts" \
  -v
```

### 5. Publish Test Message
```bash
docker exec greengrid-mqtt mosquitto_pub \
  -h localhost \
  -u greengrid \
  -P greengrid123 \
  -t "greengrid/test" \
  -m '{"test": "message", "timestamp": "2026-01-01T10:30:00Z"}'
```

## PostgreSQL (PostGIS) Queries

### 1. Connect to Database
```bash
docker exec -it greengrid-central psql -U postgres -d geospatial_db
```

### 2. Geospatial Queries

#### Get All Sites
```sql
SELECT 
    site_id,
    site_name,
    site_type,
    ST_X(location::geometry) as longitude,
    ST_Y(location::geometry) as latitude,
    capacity_kw
FROM sites;
```

#### Find Sites Within Radius (10km from center)
```sql
SELECT 
    site_id,
    site_name,
    ST_Distance(
        location,
        ST_GeogFromText('POINT(106.8456 -6.2088)')
    ) / 1000 as distance_km
FROM sites
WHERE ST_DWithin(
    location,
    ST_GeogFromText('POINT(106.8456 -6.2088)'),
    10000  -- 10km in meters
)
ORDER BY distance_km;
```

#### Get Sites by Province
```sql
SELECT 
    site_id,
    site_name,
    site_type,
    city
FROM sites
WHERE province = 'DKI Jakarta';
```

#### Calculate Total Capacity by Type
```sql
SELECT 
    site_type,
    COUNT(*) as total_sites,
    SUM(capacity_kw) as total_capacity_kw,
    AVG(capacity_kw) as avg_capacity_kw
FROM sites
GROUP BY site_type;
```

### 3. Energy Metrics Queries

#### Latest Energy Metrics per Site
```sql
SELECT DISTINCT ON (site_id)
    site_id,
    timestamp,
    total_consumption_kwh,
    solar_generation_kwh,
    battery_level_percent,
    pue_ratio
FROM energy_metrics
ORDER BY site_id, timestamp DESC;
```

#### Daily Energy Summary
```sql
SELECT 
    DATE(timestamp) as date,
    site_id,
    SUM(total_consumption_kwh) as total_consumption,
    SUM(solar_generation_kwh) as total_solar,
    AVG(battery_level_percent) as avg_battery_level
FROM energy_metrics
WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(timestamp), site_id
ORDER BY date DESC, site_id;
```

## InfluxDB Queries

### 1. Connect to InfluxDB
```bash
docker exec -it greengrid-central influx
```

### 2. Basic Queries

#### Show Databases
```sql
SHOW DATABASES;
USE telco_metrics;
```

#### Show Measurements
```sql
SHOW MEASUREMENTS;
```

#### Show Tags
```sql
SHOW TAG KEYS FROM "telco_metrics";
SHOW TAG VALUES FROM "telco_metrics" WITH KEY = "gateway_id";
```

#### Show Field Keys
```sql
SHOW FIELD KEYS FROM "telco_metrics";
```

### 3. Time-Series Queries

#### Latest Values per Gateway
```sql
SELECT 
    gateway_id,
    gateway_type,
    *
FROM telco_metrics
WHERE time > now() - 5m
GROUP BY gateway_id
ORDER BY time DESC
LIMIT 10;
```

#### Average Power Consumption (Last Hour)
```sql
SELECT 
    MEAN("energy_meter_power_total_kw") as avg_power
FROM telco_metrics
WHERE time > now() - 1h
    AND gateway_id = 'CELL_SITE_001'
GROUP BY time(5m);
```

#### Battery SOC Trends
```sql
SELECT 
    gateway_id,
    MEAN("battery_bms_soc_percent") as avg_soc,
    MIN("battery_bms_soc_percent") as min_soc,
    MAX("battery_bms_soc_percent") as max_soc
FROM telco_metrics
WHERE time > now() - 24h
GROUP BY time(1h), gateway_id;
```

#### PUE Calculation (Data Center)
```sql
SELECT 
    MEAN("pue_metrics_pue") as avg_pue,
    MEAN("pue_metrics_it_power_kw") as avg_it_power,
    MEAN("pue_metrics_cooling_power_kw") as avg_cooling_power
FROM telco_metrics
WHERE time > now() - 1h
    AND gateway_id = 'DC_SITE_001'
GROUP BY time(5m);
```

#### Temperature Monitoring
```sql
SELECT 
    gateway_id,
    MEAN("environmental_sensors_room_temp_c") as avg_temp,
    MAX("environmental_sensors_room_temp_c") as max_temp
FROM telco_metrics
WHERE time > now() - 24h
GROUP BY time(1h), gateway_id;
```

## Advanced Analytics Queries

### 1. Energy Efficiency Comparison
```sql
-- PostgreSQL
SELECT 
    s.site_id,
    s.site_name,
    s.site_type,
    AVG(em.pue_ratio) as avg_pue,
    AVG(em.solar_generation_kwh / em.total_consumption_kwh * 100) as renewable_percentage
FROM sites s
JOIN energy_metrics em ON s.site_id = em.site_id
WHERE em.timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY s.site_id, s.site_name, s.site_type
ORDER BY renewable_percentage DESC;
```

### 2. Correlation Analysis
```sql
-- InfluxDB
SELECT 
    CORR("environmental_sensors_room_temp_c", "cooling_systems_crac_1_power_kw") as temp_cooling_correlation
FROM telco_metrics
WHERE time > now() - 7d
    AND gateway_id = 'DC_SITE_001';
```

### 3. Anomaly Detection
```sql
-- InfluxDB
SELECT 
    gateway_id,
    MEAN("energy_meter_power_total_kw") as avg_power,
    STDDEV("energy_meter_power_total_kw") as power_stddev
FROM telco_metrics
WHERE time > now() - 24h
GROUP BY time(1h), gateway_id
HAVING STDDEV("energy_meter_power_total_kw") > 2.0;
```

## Python Examples

### 1. Fetch Data from API
```python
import requests
import json

# Central Platform
response = requests.get('http://localhost:8080/api/sites')
sites = response.json()
print(json.dumps(sites, indent=2))

# Edge Gateway
response = requests.get('http://localhost:8081/api/metrics')
metrics = response.json()
print(f"Current Power: {metrics['metrics']['energy_meter']['power_total_kw']} kW")
```

### 2. MQTT Subscribe
```python
import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print("Connected!")
    client.subscribe("greengrid/edge/+/metrics")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print(f"Gateway: {data['gateway_id']}")
    print(f"Power: {data['metrics'].get('energy_meter_power_total_kw', 'N/A')} kW")

client = mqtt.Client()
client.username_pw_set("greengrid", "greengrid123")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()
```

### 3. Query InfluxDB
```python
from influxdb_client import InfluxDBClient

client = InfluxDBClient(
    url="http://localhost:8086",
    token="admin:admin123",
    org="greengrid"
)

query = '''
from(bucket: "telco_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r.gateway_id == "CELL_SITE_001")
  |> filter(fn: (r) => r._field == "energy_meter_power_total_kw")
  |> mean()
'''

result = client.query_api().query(query)
for table in result:
    for record in table.records:
        print(f"Average Power: {record.get_value()} kW")
```

### 4. Query PostGIS
```python
import psycopg2
import json

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="geospatial_db",
    user="postgres",
    password="postgres123"
)

cursor = conn.cursor()
cursor.execute("""
    SELECT 
        site_id,
        site_name,
        ST_X(location::geometry) as lon,
        ST_Y(location::geometry) as lat
    FROM sites
""")

sites = cursor.fetchall()
for site in sites:
    print(f"{site[1]}: ({site[2]}, {site[3]})")

cursor.close()
conn.close()
```

## Grafana Dashboard Examples

### 1. Power Consumption Panel
```sql
-- Query
SELECT 
    mean("energy_meter_power_total_kw") 
FROM "telco_metrics" 
WHERE $timeFilter 
    AND gateway_id = '$gateway_id'
GROUP BY time($__interval)
```

### 2. Battery SOC Gauge
```sql
-- Query
SELECT 
    last("battery_bms_soc_percent") 
FROM "telco_metrics" 
WHERE $timeFilter 
    AND gateway_id = 'CELL_SITE_001'
```

### 3. PUE Trend
```sql
-- Query
SELECT 
    mean("pue_metrics_pue") 
FROM "telco_metrics" 
WHERE $timeFilter 
    AND gateway_id = 'DC_SITE_001'
GROUP BY time($__interval)
```

### 4. Site Map
```sql
-- PostgreSQL Query
SELECT 
    site_id as "metric",
    site_name as "name",
    ST_Y(location::geometry) as "latitude",
    ST_X(location::geometry) as "longitude",
    capacity_kw as "value"
FROM sites
```

## Troubleshooting Queries

### 1. Check MQTT Message Rate
```bash
# Count messages in last minute
docker exec greengrid-mqtt mosquitto_sub \
  -h localhost \
  -u greengrid \
  -P greengrid123 \
  -t "greengrid/#" \
  -C 100 | wc -l
```

### 2. Check Database Sizes
```sql
-- PostgreSQL
SELECT 
    pg_size_pretty(pg_database_size('geospatial_db')) as db_size;

-- InfluxDB
SHOW STATS;
```

### 3. Check Missing Data
```sql
-- InfluxDB
SELECT 
    COUNT(*) 
FROM telco_metrics 
WHERE time > now() - 1h 
GROUP BY gateway_id;
```

### 4. Validate Metric Ranges
```sql
-- InfluxDB
SELECT 
    gateway_id,
    MIN("energy_meter_power_total_kw") as min_power,
    MAX("energy_meter_power_total_kw") as max_power,
    MEAN("energy_meter_power_total_kw") as avg_power
FROM telco_metrics
WHERE time > now() - 24h
GROUP BY gateway_id;
```
