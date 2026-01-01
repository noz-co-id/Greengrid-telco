# Greengrid Telco - Docker Deployment Guide

## Arsitektur Sistem

Sistem Greengrid Telco terdiri dari 4 container utama:

### 1. **Central Platform Container**
- **Fungsi**: Core platform untuk mengumpulkan, menyimpan, dan menganalisis data
- **Komponen**:
  - PostgreSQL + PostGIS (Database Geospatial)
  - InfluxDB (Time-Series Database)
  - Grafana (Visualization Dashboard)
  - Analytics Engine
  - ESG/SDG Reporting
- **Ports**: 8086 (InfluxDB), 5432 (PostgreSQL), 3000 (Grafana), 8080 (API)

### 2. **MQTT Middleware Container**
- **Fungsi**: Message broker dan OpenTelemetry processor
- **Komponen**:
  - Mosquitto MQTT Broker
  - OpenTelemetry Processor
  - Metric Filtering Engine
- **Ports**: 1883 (MQTT), 9001 (WebSocket), 4317/4318 (OpenTelemetry)

### 3. **Edge Gateway A - Cell Site**
- **Fungsi**: Monitoring sel telco (2G/3G/4G/5G)
- **Protokol**: Modbus RTU
- **Capabilities**: Local Buffer, Offline Mode
- **Devices Monitored**:
  - Energy Meters
  - Battery BMS
  - Solar MPPT
  - Genset Control
  - Telco Equipment (2G/3G/4G/5G)
  - End User Meters
- **Sampling Rate**: 5 detik

### 4. **Edge Gateway B - Data Center**
- **Fungsi**: Monitoring data center telco
- **Protokol**: Modbus TCP, OPC UA
- **Capabilities**: High-frequency sampling (100ms)
- **Devices Monitored**:
  - UPS Systems
  - Cooling (CRAC units)
  - Servers
  - Network Switches
  - Power Distribution (PDU)
  - Environmental Sensors
  - PUE Metrics
- **Sampling Rate**: 100ms (high frequency)

### 5. **Edge Gateway C - Switch Room**
- **Fungsi**: Monitoring switch room telco
- **Protokol**: SNMP
- **Capabilities**: Local HMI, VPN Tunnel
- **Devices Monitored**:
  - HVAC Control
  - Power Distribution
  - Generators
  - Lighting Control
  - Environmental Sensors
  - Security Systems
  - Network Equipment
  - UPS Backup
- **Sampling Rate**: 1 detik

## Struktur Direktori

```
greengrid-telco/
├── docker-compose.yml
├── central-platform/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── start.sh
│   ├── init_db.py
│   ├── main.py
│   └── dashboards/
├── mqtt-middleware/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── start.sh
│   ├── otel_processor.py
│   └── config/
│       └── mosquitto.conf
├── edge-gateway-cell/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── start.sh
│   └── main.py
├── edge-gateway-datacenter/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── start.sh
│   └── main.py
└── edge-gateway-switchroom/
    ├── Dockerfile
    ├── requirements.txt
    ├── start.sh
    └── main.py
```

## Cara Deployment

### 1. Persiapan

```bash
# Clone repository
git clone https://github.com/noz-co-id/Greengrid-telco.git
cd Greengrid-telco

# Pastikan Docker dan Docker Compose terinstall
docker --version
docker-compose --version
```

### 2. Build dan Start Semua Container

```bash
# Build semua images
docker-compose build

# Start semua services
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Verifikasi Deployment

```bash
# Check logs central platform
docker-compose logs -f central-platform

# Check logs MQTT middleware
docker-compose logs -f mqtt-middleware

# Check logs edge gateways
docker-compose logs -f edge-gateway-cell
docker-compose logs -f edge-gateway-datacenter
docker-compose logs -f edge-gateway-switchroom
```

### 4. Akses Services

- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Central Platform API**: http://localhost:8080/api
- **MQTT Broker**: mqtt://localhost:1883 (greengrid/greengrid123)
- **Cell Site API**: http://localhost:8081/api
- **Data Center API**: http://localhost:8082/api
- **Switch Room HMI**: http://localhost:8083

## Testing Endpoints

### Central Platform

```bash
# Health check
curl http://localhost:8080/health

# Get all sites
curl http://localhost:8080/api/sites

# Get real-time metrics
curl http://localhost:8080/api/metrics/realtime

# Get ESG report
curl http://localhost:8080/api/esg/report

# Get dashboard summary
curl http://localhost:8080/api/dashboard/summary
```

### Edge Gateways

```bash
# Cell Site
curl http://localhost:8081/health
curl http://localhost:8081/api/metrics

# Data Center
curl http://localhost:8082/health
curl http://localhost:8082/api/metrics
curl http://localhost:8082/api/pue

# Switch Room
curl http://localhost:8083/health
curl http://localhost:8083/api/metrics
# Akses HMI di browser: http://localhost:8083
```

## Monitoring MQTT Traffic

```bash
# Subscribe ke semua topics
docker exec greengrid-mqtt mosquitto_sub -h localhost -u greengrid -P greengrid123 -t "greengrid/#" -v

# Subscribe ke metrics tertentu
docker exec greengrid-mqtt mosquitto_sub -h localhost -u greengrid -P greengrid123 -t "greengrid/edge/+/metrics" -v

# Subscribe ke status
docker exec greengrid-mqtt mosquitto_sub -h localhost -u greengrid -P greengrid123 -t "greengrid/edge/+/status" -v
```

## Data Flow

```
Edge Gateways → Raw Data → MQTT Middleware (Filter + OpenTelemetry) 
                         ↓
                   Filtered Metrics
                         ↓
                Central Platform → InfluxDB (Time-Series)
                         ↓         PostGIS (Geospatial)
                         ↓
                   Analytics Engine
                         ↓
                Grafana Dashboard + ESG/SDG Reports
```

## Metric Filtering Rules

### Cell Site
- **Include**: voltage, current, power, battery, solar, temperature, signal_strength, connected_users
- **Sample Rate**: 5000ms (5 detik)

### Data Center
- **Include**: voltage, current, power, temperature, humidity, cpu_usage, memory_usage, network_throughput, ups_status
- **Sample Rate**: 100ms (high frequency)

### Switch Room
- **Include**: voltage, current, power, temperature, humidity, hvac_status, door_status, fire_alarm, switch_status
- **Sample Rate**: 1000ms (1 detik)

## Stopping and Cleaning Up

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all
```

## Troubleshooting

### Container tidak start
```bash
# Check logs
docker-compose logs [service_name]

# Restart specific service
docker-compose restart [service_name]
```

### MQTT connection failed
```bash
# Check MQTT broker status
docker exec greengrid-mqtt ps aux | grep mosquitto

# Test MQTT connection
docker exec greengrid-mqtt mosquitto_pub -h localhost -u greengrid -P greengrid123 -t "test" -m "hello"
```

### Database tidak bisa diakses
```bash
# Check PostgreSQL
docker exec greengrid-central psql -U postgres -d geospatial_db -c "SELECT version();"

# Check InfluxDB
docker exec greengrid-central influx -execute "SHOW DATABASES"
```

## Scalability

Untuk menambah edge gateway baru:

1. Copy salah satu folder edge-gateway-*
2. Modifikasi environment variables di docker-compose.yml
3. Update GATEWAY_ID dan LOCATION
4. Run `docker-compose up -d [new_gateway_name]`

## Production Recommendations

1. **Security**:
   - Ganti default passwords
   - Enable SSL/TLS untuk MQTT
   - Setup firewall rules
   - Enable authentication untuk Grafana

2. **Performance**:
   - Increase buffer sizes untuk offline mode
   - Setup InfluxDB retention policies
   - Enable data compression

3. **High Availability**:
   - Setup MQTT broker clustering
   - PostgreSQL replication
   - Load balancer untuk API

4. **Monitoring**:
   - Enable Prometheus metrics
   - Setup alerting via Grafana
   - Log aggregation dengan ELK stack

## Support

Untuk pertanyaan dan support:
- GitHub Issues: https://github.com/noz-co-id/Greengrid-telco/issues
- Documentation: https://github.com/noz-co-id/Greengrid-telco/wiki
