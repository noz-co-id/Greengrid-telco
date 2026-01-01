# Greengrid Telco - System Summary

## Executive Summary

Greengrid Telco adalah sistem monitoring dan manajemen energi untuk infrastruktur telekomunikasi yang mengintegrasikan:
- Core Network Telco (2G/3G/4G/5G)
- SCADA Systems
- Renewable Energy (Solar, Battery)
- Data Center Infrastructure
- Real-time Analytics & Reporting (ESG/SDG)

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                     CENTRAL PLATFORM                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  PostgreSQL  │  │   InfluxDB   │  │   Grafana    │          │
│  │   PostGIS    │  │ Time-Series  │  │  Dashboard   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌───────────────────────────────────────────────────┐         │
│  │      Analytics Engine + ESG/SDG Reporting         │         │
│  └───────────────────────────────────────────────────┘         │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                    MQTT MIDDLEWARE                             │
│  ┌──────────────┐  ┌────────────────────────────────┐          │
│  │  Mosquitto   │  │  OpenTelemetry Processor       │          │
│  │ MQTT Broker  │  │  (Metric Filtering Engine)     │          │
│  └──────────────┘  └────────────────────────────────┘          │
└───────┬──────────────────┬──────────────────┬──────────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Edge Gateway │  │ Edge Gateway │  │ Edge Gateway │
│   CELL SITE  │  │ DATA CENTER  │  │ SWITCH ROOM  │
│              │  │              │  │              │
│ Modbus RTU   │  │ Modbus TCP   │  │    SNMP      │
│ Local Buffer │  │   OPC UA     │  │  Local HMI   │
│ Offline Mode │  │ High-Freq    │  │ VPN Tunnel   │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Component Details

### 1. Central Platform
**Technology Stack:**
- PostgreSQL 15 + PostGIS 3.x
- InfluxDB 1.8
- Grafana 10.x
- Python 3.11 (Flask)

**Key Features:**
- Geospatial database untuk lokasi sites
- Time-series storage untuk metrics
- Real-time analytics
- ESG/SDG compliance reporting
- RESTful API untuk integrasi

**API Endpoints:**
```
GET  /health                    - Health check
GET  /api/sites                 - List all sites dengan geolocation
GET  /api/metrics/realtime      - Real-time metrics data
GET  /api/esg/report            - ESG/SDG reports
GET  /api/dashboard/summary     - Dashboard summary
```

### 2. MQTT Middleware
**Technology Stack:**
- Mosquitto MQTT Broker
- OpenTelemetry (Tracing & Metrics)
- Python 3.11

**Key Features:**
- Message broker dengan QoS support
- OpenTelemetry untuk observability
- Dynamic metric filtering per gateway type
- Support WebSocket untuk web clients
- Rate limiting dan flow control

**Topic Structure:**
```
greengrid/edge/{gateway_id}/raw       - Raw data dari edge
greengrid/edge/{gateway_id}/metrics   - Filtered metrics
greengrid/edge/{gateway_id}/status    - Gateway status
greengrid/edge/{gateway_id}/alerts    - Alerts & alarms
```

### 3. Edge Gateway A - Cell Site
**Protokol:** Modbus RTU
**Sampling Rate:** 5 detik
**Location:** -6.2088, 106.8456 (Jakarta)

**Monitored Equipment:**
1. **Energy Meter** (3-phase)
   - Voltage L1/L2/L3 (V)
   - Current L1/L2/L3 (A)
   - Power Total (kW)
   - Energy Total (kWh)
   - Power Factor
   - Frequency (Hz)

2. **Battery BMS**
   - Voltage (V)
   - Current (A)
   - State of Charge (%)
   - State of Health (%)
   - Temperature (°C)
   - Charging Status
   - Cycle Count
   - Capacity (Ah)

3. **Solar MPPT**
   - PV Voltage (V)
   - PV Current (A)
   - PV Power (kW)
   - Battery Voltage (V)
   - Battery Current (A)
   - Daily Energy (kWh)
   - Total Energy (kWh)
   - MPPT Efficiency (%)

4. **Genset Control**
   - Status (standby/running)
   - Voltage (V)
   - Current (A)
   - Power (kW)
   - Frequency (Hz)
   - Fuel Level (%)
   - Runtime Hours
   - Temperature (°C)

5. **Telco Equipment** (2G/3G/4G/5G)
   - 2G/3G/4G/5G Status
   - Signal Strength (dBm)
   - Connected Users
   - Data Throughput (Mbps)
   - Equipment Temperature (°C)

6. **End User Meter**
   - Active Users
   - Total Consumption (kWh)
   - Average Power (kW)
   - Peak Power (kW)
   - Power Quality

**Special Features:**
- Local buffering (10,000 messages)
- Offline mode operation
- Automatic reconnection
- Message queuing

### 4. Edge Gateway B - Data Center
**Protokol:** Modbus TCP, OPC UA
**Sampling Rate:** 100ms (high frequency)
**Location:** -6.2293, 106.8467 (Jakarta)

**Monitored Equipment:**
1. **UPS Systems** (2 units)
   - Status (online/battery)
   - Load (%)
   - Input/Output Voltage (V)
   - Input/Output Frequency (Hz)
   - Battery Voltage (V)
   - Battery Current (A)
   - Battery SOC (%)
   - Battery Temperature (°C)
   - Estimated Runtime (min)
   - Alarms

2. **Cooling Systems** (CRAC units)
   - Status (running/stopped)
   - Supply Temperature (°C)
   - Return Temperature (°C)
   - Humidity (%)
   - Fan Speed (%)
   - Compressor Status
   - Power Consumption (kW)
   - Alarms

3. **Servers** (per rack)
   - Total/Active Servers
   - Average CPU Usage (%)
   - Average Memory Usage (%)
   - Average Disk Usage (%)
   - Inlet Temperature (°C)
   - Power Consumption (kW)
   - Network RX/TX (Gbps)

4. **Network Switches**
   - Status (active/down)
   - Uptime (hours)
   - CPU Usage (%)
   - Memory Usage (%)
   - Temperature (°C)
   - Port Utilization (%)
   - Active/Total Ports
   - Throughput (Gbps)
   - Packet Loss (%)
   - Errors

5. **Power Distribution** (PDU)
   - Voltage L1/L2/L3 (V)
   - Current L1/L2/L3 (A)
   - Power Total (kW)
   - Energy (kWh)
   - Power Factor

6. **Environmental Sensors**
   - Hot Aisle Temperature (°C)
   - Cold Aisle Temperature (°C)
   - Ambient Humidity (%)
   - Differential Pressure (Pa)
   - Smoke Detector Status
   - Water Leak Detector Status

7. **PUE Metrics**
   - PUE Ratio
   - IT Power (kW)
   - Total Facility Power (kW)
   - Cooling Power (kW)
   - Lighting Power (kW)
   - Other Power (kW)

**Special Features:**
- High-frequency sampling (100ms)
- Real-time PUE calculation
- Thermal management monitoring
- Network performance tracking

### 5. Edge Gateway C - Switch Room
**Protokol:** SNMP
**Sampling Rate:** 1 detik
**Location:** -6.2145, 106.8489 (Jakarta)

**Monitored Equipment:**
1. **HVAC Control** (2 units)
   - Status (running/stopped)
   - Mode (cooling/heating)
   - Setpoint Temperature (°C)
   - Current Temperature (°C)
   - Humidity (%)
   - Fan Speed (%)
   - Power Consumption (kW)
   - Compressor Status
   - Filter Status
   - Runtime Hours

2. **Power Distribution**
   - Main Breaker Status
   - Voltage L1/L2/L3 (V)
   - Current L1/L2/L3 (A)
   - Power Total (kW)
   - Frequency (Hz)
   - Power Factor
   - Sub-panel Load (%)
   - Sub-panel Power (kW)

3. **Generators**
   - Status (standby/running)
   - Voltage (V)
   - Frequency (Hz)
   - Power (kW)
   - Fuel Level (%)
   - Fuel Consumption (l/h)
   - Engine Temperature (°C)
   - Battery Voltage (V)
   - Runtime Hours
   - Last Maintenance Hours
   - Alarms

4. **Lighting Control**
   - Zone Status (on/off)
   - Brightness (%)
   - Power Consumption (W)
   - Occupancy Detection
   - Schedule Status
   - Emergency Lights Status
   - Emergency Battery (%)

5. **Environmental Sensors**
   - Room Temperature (°C)
   - Room Humidity (%)
   - Smoke Detectors (multiple)
   - CO2 Level (ppm)
   - Air Quality Index

6. **Security Systems**
   - Door Status (closed/open)
   - Door Lock Status
   - Access Count
   - Last Access Time
   - Motion Detector Status
   - CCTV Status
   - Fire Alarm Status
   - Water Leak Status

7. **Network Equipment**
   - Core Router Status
   - Router CPU/Memory (%)
   - Router Temperature (°C)
   - Router Uptime (hours)
   - Active Interfaces
   - Throughput (Mbps)
   - Aggregation Switches (2 units)
   - Switch CPU/Memory/Temp
   - Active Ports
   - Switch Throughput

8. **UPS Backup**
   - Status (online/battery)
   - Load (%)
   - Battery SOC (%)
   - Input/Output Voltage (V)
   - Estimated Runtime (min)
   - Temperature (°C)

**Special Features:**
- Local HMI web interface
- VPN tunnel support
- SNMP polling
- Security monitoring
- Environmental control

## Data Flow & Processing

### 1. Data Collection
```
Edge Gateway → Generate Metrics → MQTT Publish (Raw Data)
               ↓
            Local Buffer (if offline)
```

### 2. Data Processing
```
MQTT Raw Data → OpenTelemetry Processor
                ↓
             Filter by Gateway Type
                ↓
             Apply Sample Rate
                ↓
             Enrich with Metadata
                ↓
             MQTT Publish (Filtered)
```

### 3. Data Storage
```
Filtered Data → Central Platform
                ↓
         ┌──────┴──────┐
         ↓             ↓
    InfluxDB      PostgreSQL
   (Metrics)     (Geospatial)
```

### 4. Analytics & Visualization
```
Stored Data → Analytics Engine → Grafana Dashboard
              ↓                   ↓
           ESG/SDG Reports    Real-time Monitoring
```

## Metric Filtering Strategy

### Cell Site Metrics
**Included:**
- voltage, current, power (electrical)
- battery (SOC, voltage, current, temp)
- solar (generation, efficiency)
- temperature (ambient, equipment)
- signal_strength (RF)
- connected_users (telco)

**Filtered Out:**
- Detailed diagnostics
- Debug information
- Maintenance logs

**Rationale:** Focus on energy management and service availability

### Data Center Metrics
**Included:**
- voltage, current, power (all systems)
- temperature, humidity (environmental)
- cpu_usage, memory_usage (compute)
- network_throughput (connectivity)
- ups_status (availability)

**Filtered Out:**
- Application-level metrics
- Detailed process information
- Security logs

**Rationale:** Focus on infrastructure efficiency (PUE) and availability

### Switch Room Metrics
**Included:**
- voltage, current, power (electrical)
- temperature, humidity (environmental)
- hvac_status (cooling)
- door_status (security)
- fire_alarm (safety)
- switch_status (network)

**Filtered Out:**
- Detailed switch configurations
- Access logs
- Video feeds

**Rationale:** Focus on facility management and critical infrastructure

## ESG/SDG Reporting

### Environmental Metrics
- Total Energy Consumption (MWh)
- Renewable Energy Percentage (%)
- Carbon Emissions (tons CO2)
- Water Usage (m³)
- Waste Recycled (%)
- PUE (Data Center Efficiency)

### Social Metrics
- Total Sites
- Communities Served
- Jobs Created
- Local Procurement (%)

### Governance Metrics
- Compliance Rate (%)
- Safety Incidents
- Training Hours

### SDG Alignment
- **SDG 7**: Affordable and Clean Energy
- **SDG 9**: Industry, Innovation and Infrastructure
- **SDG 11**: Sustainable Cities and Communities
- **SDG 13**: Climate Action

## Performance Characteristics

### Latency
- Cell Site: ~5 seconds (measurement to dashboard)
- Data Center: ~100ms (high frequency)
- Switch Room: ~1 second

### Throughput
- Messages per second: ~30 (all gateways combined)
- Data volume: ~50 KB/s uncompressed
- MQTT QoS: 0-1 depending on criticality

### Scalability
- Supports 100+ edge gateways
- Millions of data points per day
- Horizontal scaling via container orchestration

### Reliability
- Local buffering at edge
- Automatic reconnection
- Data persistence
- High availability MQTT

## Security Considerations

### Authentication
- MQTT username/password
- API token-based auth
- VPN for remote access

### Authorization
- Role-based access control
- Gateway-specific credentials
- API key scoping

### Data Protection
- TLS/SSL for MQTT (production)
- Encrypted at rest (database)
- Secure credential storage

### Network Security
- Firewall rules
- VPN tunneling (Switch Room)
- Network segmentation

## Deployment

### Quick Start
```bash
chmod +x quickstart.sh
./quickstart.sh
```

### Manual Deployment
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Testing
```bash
# Run test suite
bash test-deployment.sh

# Monitor MQTT
python3 monitor-mqtt.py
```

## Maintenance

### Backup
```bash
# Backup PostgreSQL
docker exec greengrid-central pg_dump -U postgres geospatial_db > backup.sql

# Backup InfluxDB
docker exec greengrid-central influxd backup -portable /backup
```

### Update
```bash
# Pull latest images
docker-compose pull

# Rebuild
docker-compose up -d --build
```

### Monitoring
```bash
# Container stats
docker stats

# Disk usage
docker system df

# Network activity
docker network inspect greengrid-network
```

## Future Enhancements

1. **Machine Learning Integration**
   - Predictive maintenance
   - Anomaly detection
   - Load forecasting

2. **Advanced Analytics**
   - Trend analysis
   - Correlation studies
   - What-if scenarios

3. **Mobile App**
   - Real-time notifications
   - Remote control
   - Mobile dashboard

4. **Integration APIs**
   - Third-party systems
   - ERP integration
   - Billing systems

5. **Edge AI**
   - Local decision making
   - Autonomous operations
   - Smart optimization

## Support & Documentation

- **GitHub**: https://github.com/noz-co-id/Greengrid-telco
- **Issues**: https://github.com/noz-co-id/Greengrid-telco/issues
- **Wiki**: https://github.com/noz-co-id/Greengrid-telco/wiki
- **Discussions**: https://github.com/noz-co-id/Greengrid-telco/discussions

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-01  
**License**: MIT
