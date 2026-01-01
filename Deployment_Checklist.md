# Greengrid Telco - Deployment Checklist

## Pre-Deployment

### System Requirements
- [ ] Docker 20.10+ installed
- [ ] Docker Compose 2.0+ installed
- [ ] Minimum 8GB RAM available
- [ ] Minimum 50GB disk space
- [ ] Ports available: 1883, 3000, 4317, 4318, 5020, 5432, 8080-8083, 9001
- [ ] Network connectivity for container communication

### File Structure
```
greengrid-telco/
├── [ ] docker-compose.yml
├── [ ] README.md
├── [ ] SYSTEM_SUMMARY.md
├── [ ] DEPLOYMENT_CHECKLIST.md
├── [ ] quickstart.sh (chmod +x)
├── [ ] test-deployment.sh (chmod +x)
├── [ ] monitor-mqtt.py
│
├── central-platform/
│   ├── [ ] Dockerfile
│   ├── [ ] requirements.txt
│   ├── [ ] start.sh (chmod +x)
│   ├── [ ] init_db.py
│   └── [ ] main.py
│
├── mqtt-middleware/
│   ├── [ ] Dockerfile
│   ├── [ ] requirements.txt
│   ├── [ ] start.sh (chmod +x)
│   ├── [ ] otel_processor.py
│   └── config/
│       └── [ ] mosquitto.conf
│
├── edge-gateway-cell/
│   ├── [ ] Dockerfile
│   ├── [ ] requirements.txt
│   ├── [ ] start.sh (chmod +x)
│   └── [ ] main.py
│
├── edge-gateway-datacenter/
│   ├── [ ] Dockerfile
│   ├── [ ] requirements.txt
│   ├── [ ] start.sh (chmod +x)
│   └── [ ] main.py
│
└── edge-gateway-switchroom/
    ├── [ ] Dockerfile
    ├── [ ] requirements.txt
    ├── [ ] start.sh (chmod +x)
    └── [ ] main.py
```

## Deployment Steps

### 1. Initial Setup
- [ ] Clone or create project directory
- [ ] Copy all files to correct locations
- [ ] Verify all Dockerfiles are present
- [ ] Verify all requirements.txt files are present
- [ ] Make all .sh files executable: `chmod +x **/*.sh *.sh`

### 2. Configuration Review
- [ ] Review docker-compose.yml environment variables
- [ ] Verify MQTT credentials (default: greengrid/greengrid123)
- [ ] Verify database credentials
- [ ] Check gateway IDs and locations
- [ ] Verify port mappings

### 3. Build Phase
```bash
# Build all images
- [ ] docker-compose build

# Expected output:
#   ✓ central-platform    (success)
#   ✓ mqtt-middleware     (success)
#   ✓ edge-gateway-cell   (success)
#   ✓ edge-gateway-datacenter (success)
#   ✓ edge-gateway-switchroom (success)
```

### 4. Start Services
```bash
# Start all services
- [ ] docker-compose up -d

# Verify containers are running
- [ ] docker-compose ps

# Expected: 5 containers in "Up" state
```

### 5. Wait for Initialization
```bash
# Wait 30-60 seconds for services to initialize
- [ ] Sleep 30-60 seconds
- [ ] Check logs: docker-compose logs -f
```

## Post-Deployment Verification

### Container Health
```bash
- [ ] docker-compose ps | grep "Up"
      # Expected: All 5 containers show "Up"
      
- [ ] docker stats --no-stream
      # Verify CPU and memory usage are reasonable
```

### Service Connectivity

#### Central Platform
```bash
- [ ] curl http://localhost:8080/health
      # Expected: {"status": "healthy", ...}
      
- [ ] curl http://localhost:8080/api/sites
      # Expected: {"sites": [...]}
      
- [ ] curl http://localhost:3000
      # Expected: Grafana login page
```

#### MQTT Middleware
```bash
- [ ] docker exec greengrid-mqtt mosquitto_pub -h localhost -u greengrid -P greengrid123 -t "test" -m "ping"
      # Expected: No error
      
- [ ] docker exec greengrid-mqtt mosquitto_sub -h localhost -u greengrid -P greengrid123 -t "test" -C 1
      # Expected: Receives "ping"
```

#### Edge Gateway - Cell
```bash
- [ ] curl http://localhost:8081/health
      # Expected: {"gateway_id": "CELL_SITE_001", "status": "online", ...}
      
- [ ] curl http://localhost:8081/api/metrics
      # Expected: Metrics JSON with energy_meter, battery_bms, etc.
```

#### Edge Gateway - Data Center
```bash
- [ ] curl http://localhost:8082/health
      # Expected: {"gateway_id": "DC_SITE_001", "status": "online", ...}
      
- [ ] curl http://localhost:8082/api/pue
      # Expected: {"pue": 1.45, ...}
```

#### Edge Gateway - Switch Room
```bash
- [ ] curl http://localhost:8083/health
      # Expected: {"gateway_id": "SR_SITE_001", "status": "online", ...}
      
- [ ] curl http://localhost:8083
      # Expected: HTML HMI interface
      
- [ ] Open http://localhost:8083 in browser
      # Expected: Switch Room HMI dashboard visible
```

### Data Flow Verification

#### MQTT Message Flow
```bash
- [ ] Subscribe to all metrics:
      docker exec greengrid-mqtt mosquitto_sub -h localhost -u greengrid -P greengrid123 -t "greengrid/edge/+/metrics" -C 10
      
      # Expected: Receive 10 messages from different gateways
      # Cell: ~5 seconds interval
      # DC: ~100ms interval  
      # SR: ~1 second interval
```

#### Database Storage
```bash
- [ ] Check PostgreSQL:
      docker exec greengrid-central psql -U postgres -d geospatial_db -c "SELECT COUNT(*) FROM sites;"
      # Expected: count = 3
      
- [ ] Check InfluxDB:
      docker exec greengrid-central influx -execute "SHOW DATABASES" | grep telco_metrics
      # Expected: telco_metrics database exists
```

#### Metric Filtering
```bash
- [ ] Subscribe to raw data:
      docker exec greengrid-mqtt mosquitto_sub -h localhost -u greengrid -P greengrid123 -t "greengrid/edge/CELL_SITE_001/raw" -C 1
      # Expected: Raw metrics with all fields
      
- [ ] Subscribe to filtered data:
      docker exec greengrid-mqtt mosquitto_sub -h localhost -u greengrid -P greengrid123 -t "greengrid/edge/CELL_SITE_001/metrics" -C 1
      # Expected: Filtered metrics with only relevant fields
      
- [ ] Verify filtering worked (filtered < raw in terms of fields)
```

## Testing Checklist

### Automated Tests
```bash
- [ ] Run test suite:
      bash test-deployment.sh
      
      # Expected output:
      # ✓ Central Platform Health Check
      # ✓ Central Platform Sites API
      # ✓ Cell Site Health
      # ✓ Data Center Health
      # ✓ Switch Room Health
      # ✓ MQTT Broker
```

### Manual Tests

#### Test 1: Real-time Monitoring
```bash
- [ ] Start MQTT monitor:
      python3 monitor-mqtt.py
      
- [ ] Verify receiving messages from all 3 gateways
- [ ] Verify statistics counter increments
- [ ] Stop with Ctrl+C and verify final statistics
```

#### Test 2: API Integration
```bash
- [ ] Fetch dashboard summary:
      curl http://localhost:8080/api/dashboard/summary | jq '.'
      
- [ ] Verify data looks reasonable:
      - [ ] total_sites = 3
      - [ ] active_gateways = 3
      - [ ] total_power_kw > 0
      - [ ] renewable_percentage between 0-100
```

#### Test 3: ESG Reporting
```bash
- [ ] Generate ESG report:
      curl http://localhost:8080/api/esg/report | jq '.'
      
- [ ] Verify report contains:
      - [ ] environmental metrics
      - [ ] social metrics
      - [ ] governance metrics
      - [ ] sdg_alignment
```

#### Test 4: Grafana Dashboard
```bash
- [ ] Open http://localhost:3000
- [ ] Login with admin/admin
- [ ] Change password when prompted
- [ ] Verify InfluxDB datasource is configured
- [ ] Verify PostgreSQL datasource is configured
- [ ] Create test dashboard
- [ ] Add panel with query: SELECT * FROM telco_metrics LIMIT 10
- [ ] Verify data appears
```

#### Test 5: Local HMI
```bash
- [ ] Open http://localhost:8083 in browser
- [ ] Verify HMI loads
- [ ] Check all equipment cards are visible:
      - [ ] HVAC Systems
      - [ ] Power Distribution
      - [ ] Generator
      - [ ] Lighting Control
      - [ ] Environmental
      - [ ] Security
      - [ ] Network Equipment
      - [ ] UPS Backup
- [ ] Verify auto-refresh works (wait 5 seconds)
```

#### Test 6: Offline Mode (Cell Site)
```bash
- [ ] Stop MQTT middleware:
      docker-compose stop mqtt-middleware
      
- [ ] Verify Cell Site enters offline mode:
      docker-compose logs edge-gateway-cell | grep "Offline mode"
      
- [ ] Wait 30 seconds (buffer should fill)
      
- [ ] Restart MQTT middleware:
      docker-compose start mqtt-middleware
      
- [ ] Verify Cell Site reconnects and sends buffered messages:
      docker-compose logs edge-gateway-cell | grep "Sending.*buffered messages"
```

#### Test 7: High-Frequency Sampling (Data Center)
```bash
- [ ] Subscribe to DC metrics:
      docker exec greengrid-mqtt mosquitto_sub -h localhost -u greengrid -P greengrid123 -t "greengrid/edge/DC_SITE_001/metrics" -C 100
      
- [ ] Count messages received in 10 seconds
      # Expected: ~100 messages (100ms sampling = 10 msg/sec)
      
- [ ] Verify metrics include high-frequency data:
      - [ ] UPS load fluctuations
      - [ ] Temperature variations
      - [ ] Power consumption
```

## Performance Verification

### Resource Usage
```bash
- [ ] Check CPU usage:
      docker stats --no-stream | awk '{print $1, $3}'
      # Expected: All containers < 50% CPU
      
- [ ] Check memory usage:
      docker stats --no-stream | awk '{print $1, $7}'
      # Expected: All containers < 2GB RAM
      
- [ ] Check disk usage:
      docker system df
      # Expected: Total < 10GB
```

### Message Throughput
```bash
- [ ] Count MQTT messages per minute:
      timeout 60 docker exec greengrid-mqtt mosquitto_sub -h localhost -u greengrid -P greengrid123 -t "greengrid/#" | wc -l
      
      # Expected range: 600-800 messages/minute
      # Cell: ~12 msg/min (5s interval)
      # DC: ~600 msg/min (100ms interval)
      # SR: ~60 msg/min (1s interval)
```

### Latency Check
```bash
- [ ] Measure end-to-end latency:
      # Publish test message with timestamp
      # Subscribe and compare with receive timestamp
      # Expected: < 1 second total latency
```

## Security Checklist

### Access Control
- [ ] Change default MQTT credentials in production
- [ ] Change default database passwords in production
- [ ] Configure Grafana admin password
- [ ] Restrict port access via firewall
- [ ] Enable TLS/SSL for MQTT in production
- [ ] Enable HTTPS for APIs in production

### Network Security
- [ ] Configure Docker network isolation
- [ ] Setup VPN for remote access (if needed)
- [ ] Configure firewall rules
- [ ] Enable authentication for all services
- [ ] Review and restrict container capabilities

### Data Security
- [ ] Enable encryption at rest for databases
- [ ] Configure backup retention policies
- [ ] Setup automated backups
- [ ] Test backup restoration
- [ ] Implement audit logging

## Production Readiness

### High Availability
- [ ] Setup MQTT broker clustering
- [ ] Configure PostgreSQL replication
- [ ] Setup InfluxDB HA
- [ ] Configure load balancer
- [ ] Test failover scenarios

### Monitoring
- [ ] Setup Prometheus for metrics
- [ ] Configure Grafana alerts
- [ ] Setup log aggregation (ELK/Loki)
- [ ] Configure email/SMS notifications
- [ ] Create runbooks for common issues

### Backup & Recovery
- [ ] Schedule automated PostgreSQL backups
- [ ] Schedule automated InfluxDB backups
- [ ] Test backup restoration procedure
- [ ] Document recovery procedures
- [ ] Setup off-site backup storage

### Documentation
- [ ] Document architecture decisions
- [ ] Create API documentation
- [ ] Write deployment runbook
- [ ] Document troubleshooting steps
- [ ] Create user guides

## Maintenance Schedule

### Daily
- [ ] Check container health
- [ ] Monitor disk space
- [ ] Review error logs
- [ ] Check MQTT message rate

### Weekly
- [ ] Review performance metrics
- [ ] Analyze ESG reports
- [ ] Check backup status
- [ ] Update security patches

### Monthly
- [ ] Full system backup
- [ ] Performance optimization review
- [ ] Security audit
- [ ] Capacity planning review

## Rollback Procedure

If deployment fails:

1. [ ] Stop all containers: `docker-compose down`
2. [ ] Check logs: `docker-compose logs`
3. [ ] Identify failing component
4. [ ] Fix configuration or code
5. [ ] Rebuild specific service: `docker-compose build [service]`
6. [ ] Restart: `docker-compose up -d`
7. [ ] Re-run verification steps

## Sign-Off

### Deployment Team
- [ ] Deployment executed by: _______________
- [ ] Date: _______________
- [ ] All checklist items verified: _______________

### Stakeholder Approval
- [ ] Technical Lead approval: _______________
- [ ] Operations approval: _______________
- [ ] Security approval: _______________

---

**Deployment Status**: [ ] PENDING / [ ] IN PROGRESS / [ ] COMPLETE / [ ] FAILED

**Notes**:
_____________________________________________
_____________________________________________
_____________________________________________
