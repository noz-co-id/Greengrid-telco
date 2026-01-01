# 📋 RINGKASAN LENGKAP SISTEM GREENGRID TELCO
## 🏗️ Arsitektur :
### 1. Central Platform Container
- PostgreSQL + PostGIS (database geospatial)
- InfluxDB (time-series database)
- Grafana (visualisasi)
- Analytics Engine
- ESG/SDG Reporting
- Port: 8086, 5432, 3000, 8080

### 2. MQTT Middleware Container
- Mosquitto MQTT Broker
- OpenTelemetry Processor untuk filtering metrics
- Metric filtering berdasarkan tipe gateway
- Port: 1883, 9001, 4317, 4318

### 3. Edge Gateway A - CELL SITE
- Protokol: Modbus RTU
- Capabilities: Local Buffer, Offline Mode


Monitoring:
- Energy Meters (3-phase, power, voltage, current)
- Battery BMS (SOC, voltage, temperature)
- Solar MPPT (generation, efficiency)
- Genset Control
- Telco Equipment (2G/3G/4G/5G, signal strength, users)
- End User Meters
- Sampling: 5 detik
- Port: 8081

4. Edge Gateway B - DATA CENTER
- Protokol: Modbus TCP, OPC UA
- Capabilities: High-frequency sampling (100ms)

Monitoring:
- UPS Systems (load, battery, runtime)
- Cooling (CRAC, temperature, humidity)
- Servers (CPU, memory, temperature)
- Network Switches (throughput, ports)
- Power Distribution (PDU)
- Environmental Sensors
- PUE Metrics (real-time calculation)
- Sampling: 100ms (high frequency)
- Port: 8082

### 5. Edge Gateway C - SWITCH ROOM
- Protokol: SNMP
- Capabilities: Local HMI, VPN Tunnel

Monitoring:
- HVAC Control (temperature, humidity)
- Power Distribution
- Generators (fuel, status)
- Lighting Control
- Environmental Sensors
- Security Systems (doors, CCTV, fire alarm)
- Network Equipment (routers, switches)
- UPS Backup
- Sampling: 1 detik
- Port: 8083 (with web HMI)

## ✨ Fitur Khusus:
### Data Generator yang Realistis:
- Semua edge gateway menghasilkan data dummy yang realistis
- Variasi berdasarkan waktu (solar generation berbeda siang/malam)
- Fluktuasi natural pada semua metrics
- Data mengikuti pola real-world

### OpenTelemetry Filtering:
- Middleware menyaring metrics berdasarkan tipe gateway
- Cell: focus pada energy & telco metrics
- DC: focus pada infrastructure & PUE
- SR: focus pada facility management
- Sampling rate disesuaikan per gateway

### Offline Mode (Cell Site):
- Buffer lokal 10,000 messages
- Auto-reconnect saat koneksi pulih
- Mengirim buffered messages saat online

### High-Frequency Sampling (Data Center):
- Sampling 100ms untuk monitoring detail
- Real-time PUE calculation
- Thermal management tracking

### Local HMI (Switch Room):
- Web interface di port 8083
Real-time monitoring semua equipment
Auto-refresh setiap 5 detik
Color-coded status indicators

```bash
# Quick start (one command)
chmod +x quickstart.sh
./quickstart.sh

# Manual
docker-compose build
docker-compose up -d

# Testing
bash test-deployment.sh
python3 monitor-mqtt.py
```
### 📊 Akses Services:

- Grafana: http://localhost:3000 (admin/admin)
- Central API: http://localhost:8080/api
- Cell Site: http://localhost:8081/api
- Data Center: http://localhost:8082/api
- Switch Room HMI: http://localhost:8083
