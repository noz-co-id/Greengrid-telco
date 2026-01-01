# Telco Core Network Protocols - Implementation Guide

## Overview

Sistem Greengrid Telco sekarang dilengkapi dengan **Telco Core Network Simulator** yang mengemulasikan protokol standar industri untuk 2G, 3G, 4G, dan 5G networks.

## Arsitektur Telco Core Network

```text
┌─────────────────────────────────────────────────────────────────┐
│                   TELCO CORE NETWORK STACK                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐              │
│  │  2G    │   │  3G    │   │  4G    │   │  5G    │              │
│  │  GSM   │   │  UMTS  │   │  LTE   │   │  NR    │              │
│  └────────┘   └────────┘   └────────┘   └────────┘              │
│      │            │            │            │                   │
│      ├─ MAP       ├─ RANAP     ├─ S1AP      ├─ NGAP             │
│      ├─ ISUP      ├─ GTP       ├─ GTPv2     ├─ NAS-5G           │
│      └─ A-IF      ├─ GMM       ├─ X2AP      ├─ PFCP             │
│                   └─ Diameter  └─ Diameter  └─ HTTP/2           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 1. 2G (GSM) Core Network

### Components
- **MSC** (Mobile Switching Center) - Call routing & switching
- **HLR** (Home Location Register) - Subscriber database
- **VLR** (Visitor Location Register) - Temporary subscriber data
- **AuC** (Authentication Center) - Security & authentication

### Protocols Implemented

#### MAP (Mobile Application Part)
```python
# Location Update Procedure
{
  "protocol": "MAP",
  "procedure": "UpdateLocation",
  "imsi": "510101234567890",
  "msisdn": "+628121234567",
  "lai": {
    "mcc": "510",
    "mnc": "10",
    "lac": 1234
  },
  "vlr_number": "VLR-01"
}
```

**Use Cases:**
- Location updates
- SMS routing
- Subscriber authentication
- Call forwarding setup

#### ISUP (ISDN User Part)
```python
# Call Setup
{
  "protocol": "ISUP",
  "procedure": "InitialAddressMessage",
  "call_id": "CALL-000001",
  "calling_party": "+628121234567",
  "called_party": "+628129876543",
  "service_type": "voice"
}
```

**Use Cases:**
- Voice call setup
- Call teardown
- Circuit switching

### Metrics Generated
- Active calls
- Location updates per second
- Call success rate
- Average call duration
- SMS throughput

---

## 2. 3G (UMTS) Core Network

### Components
- **MSC** - Circuit-switched voice
- **SGSN** (Serving GPRS Support Node) - Packet-switched data
- **GGSN** (Gateway GPRS Support Node) - Internet gateway
- **HLR** - Subscriber database

### Protocols Implemented

#### RANAP (Radio Access Network Application Part)
```python
# GPRS Attach
{
  "protocol": "GMM",
  "procedure": "AttachRequest",
  "imsi": "510101234567890",
  "rai": {
    "mcc": "510",
    "mnc": "10",
    "lac": 1234,
    "rac": "001"
  },
  "attach_type": "combined"
}
```

#### GTP (GPRS Tunneling Protocol)
```python
# PDP Context Activation
{
  "protocol": "GTP",
  "procedure": "CreatePDPContextRequest",
  "imsi": "510101234567890",
  "teid": 123456,
  "apn": "internet",
  "qos": {
    "traffic_class": "interactive",
    "max_bitrate_ul": 384,  # kbps
    "max_bitrate_dl": 384
  },
  "allocated_ip": "10.1.2.3"
}
```

**Tunnel Types:**
- GTP-C (Control plane) - Port 2123
- GTP-U (User plane) - Port 2152

### Metrics Generated
- Active PDP contexts
- Data throughput (UL/DL)
- Attach success rate
- Bearer setup time
- QoS compliance

---

## 3. 4G (LTE/EPC) Core Network

### Components (EPC - Evolved Packet Core)
- **MME** (Mobility Management Entity) - Signaling & mobility
- **SGW** (Serving Gateway) - User plane routing
- **PGW** (PDN Gateway) - Internet connectivity
- **HSS** (Home Subscriber Server) - Subscriber data
- **PCRF** (Policy Control & Charging Rules)

### Protocols Implemented

#### S1AP (S1 Application Protocol)
```python
# Initial Attach
{
  "protocol": "S1AP",
  "procedure": "InitialUEMessage",
  "imsi": "510101234567890",
  "guti": {
    "mcc": "510",
    "mnc": "10",
    "mme_group_id": 1,
    "mme_code": 1,
    "m_tmsi": 1234567
  },
  "ecgi": {
    "mcc": "510",
    "mnc": "10",
    "cell_id": 12345
  },
  "ue_capability": {
    "category": "Cat6",
    "max_dl_bitrate": 300,  # Mbps
    "max_ul_bitrate": 50
  }
}
```

#### GTPv2 (GTP version 2)
```python
# Bearer Setup
{
  "protocol": "GTPv2",
  "procedure": "CreateSessionRequest",
  "imsi": "510101234567890",
  "ebi": 5,  # EPS Bearer ID
  "s1u_teid": 123456,
  "s5_teid": 789012,
  "apn": "internet",
  "qci": 9,  # QoS Class Identifier
  "arp": {
    "priority_level": 8,
    "pre_emption_capability": "disabled"
  },
  "ue_ip_address": "10.1.2.3"
}
```

**QCI (QoS Class Identifier) Values:**
- QCI 1: Conversational Voice
- QCI 2: Conversational Video
- QCI 5: IMS Signaling
- QCI 9: Default Bearer

#### X2AP (X2 Application Protocol)
```python
# Handover between eNodeBs
{
  "protocol": "X2AP",
  "procedure": "HandoverRequest",
  "imsi": "510101234567890",
  "source_cell_id": 12345,
  "target_cell_id": 12346,
  "handover_type": "intra_lte",
  "cause": "radio_connection_with_ue_lost"
}
```

### LTE Interfaces
- **S1-MME**: eNodeB ↔ MME (control plane)
- **S1-U**: eNodeB ↔ SGW (user plane)
- **S5/S8**: SGW ↔ PGW
- **S6a**: MME ↔ HSS (Diameter)
- **S11**: MME ↔ SGW (GTPv2-C)
- **X2**: eNodeB ↔ eNodeB (handover)

### Metrics Generated
- Active EPS bearers
- Attach success rate
- Handover success rate
- E-RAB setup success rate
- Packet loss rate
- Latency (ms)

---

## 4. 5G (NR) Core Network

### Components (5GC - 5G Core)
- **AMF** (Access & Mobility Management) - Connection & mobility
- **SMF** (Session Management Function) - Session management
- **UPF** (User Plane Function) - Packet routing
- **UDM** (Unified Data Management) - Subscriber data
- **PCF** (Policy Control Function) - Policy rules
- **AUSF** (Authentication Server Function) - Authentication
- **NSSF** (Network Slice Selection Function) - Slicing

### Service-Based Architecture (SBA)
5G menggunakan **Service-Based Architecture** dengan HTTP/2:
- Namf (AMF services)
- Nsmf (SMF services)
- Npcf (PCF services)
- Nudm (UDM services)

### Protocols Implemented

#### NGAP (NG Application Protocol)
```python
# 5G Registration
{
  "protocol": "NGAP",
  "procedure": "InitialUEMessage",
  "service_type": "5GMM",
  "imsi": "510101234567890",
  "guti_5g": {
    "mcc": "510",
    "mnc": "10",
    "amf_region_id": 1,
    "amf_set_id": 1,
    "amf_pointer": 0,
    "tmsi_5g": 12345678
  },
  "ncgi": {
    "mcc": "510",
    "mnc": "10",
    "nr_cell_id": 123456
  },
  "ue_capability": {
    "nr_bands": ["n1", "n3", "n78"],
    "max_dl_bitrate_gbps": 10,
    "max_ul_bitrate_gbps": 5,
    "slice_support": true
  }
}
```

#### NAS-5G (Non-Access Stratum)
```python
# PDU Session Establishment
{
  "protocol": "NAS-5G",
  "procedure": "PDUSessionEstablishmentRequest",
  "imsi": "510101234567890",
  "pdu_session_id": 1,
  "s_nssai": {
    "sst": 1,  # Slice/Service Type
    "sd": "000001"  # Slice Differentiator
  },
  "dnn": "internet",  # Data Network Name
  "pdu_session_type": "IPv6",
  "qos_flow": {
    "qfi": 1,  # QoS Flow Identifier
    "5qi": 9,  # 5G QoS Identifier
    "gfbr": 10,  # Guaranteed Flow Bit Rate (Mbps)
    "mfbr": 100  # Maximum Flow Bit Rate (Mbps)
  },
  "ue_ip_address": "2001:db8:1::1"
}
```

### 5G Service Types

#### 1. eMBB (Enhanced Mobile Broadband)
```python
{
  "service_type": "eMBB",
  "service_parameters": {
    "latency_ms": 10,
    "reliability": "99.9%",
    "throughput_gbps": 10
  },
  "network_slice": {
    "sst": 1,
    "slice_name": "eMBB"
  }
}
```

**Use Cases:**
- 4K/8K video streaming
- AR/VR applications
- Cloud gaming

#### 2. URLLC (Ultra-Reliable Low-Latency)
```python
{
  "service_type": "URLLC",
  "service_parameters": {
    "latency_ms": 1,
    "reliability": "99.999%",
    "throughput_mbps": 10
  },
  "network_slice": {
    "sst": 2,
    "slice_name": "URLLC"
  }
}
```

**Use Cases:**
- Industrial automation
- Autonomous vehicles
- Remote surgery
- Factory automation

#### 3. mMTC (Massive Machine-Type Communications)
```python
{
  "service_type": "mMTC",
  "service_parameters": {
    "latency_ms": 1000,
    "reliability": "99%",
    "connection_density": "1M_per_km2"
  },
  "network_slice": {
    "sst": 3,
    "slice_name": "mMTC"
  }
}
```

**Use Cases:**
- Smart cities
- IoT sensors
- Smart meters
- Agricultural monitoring

### 5G Network Slicing
```
┌──────────────────────────────────────────┐
│         5G Network Slicing               │
├──────────────────────────────────────────┤
│                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │  eMBB   │  │  URLLC  │  │  mMTC   │   │
│  │ Slice 1 │  │ Slice 2 │  │ Slice 3 │   │
│  └─────────┘  └─────────┘  └─────────┘   │
│       │            │            │        │
│       └────────────┴────────────┘        │
│                    │                     │
│              ┌──────────┐                │
│              │  Shared  │                │
│              │   UPF    │                │
│              └──────────┘                │
└──────────────────────────────────────────┘
```

### 5G Interfaces
- **N1**: UE ↔ AMF (NAS)
- **N2**: gNB ↔ AMF (NGAP)
- **N3**: gNB ↔ UPF (user plane)
- **N4**: SMF ↔ UPF (PFCP)
- **N6**: UPF ↔ Data Network
- **Namf**: Service-based (HTTP/2)

### Metrics Generated
- Active PDU sessions
- Network slice utilization
- Service type distribution (eMBB/URLLC/mMTC)
- 5G KPIs (latency, throughput, reliability)
- Slice-specific metrics

---

## API Endpoints

### Get Telco Statistics
```bash
curl http://localhost:8080/api/telco/statistics | jq '.'
```

**Response:**
```json
{
  "timestamp": "2026-01-01T10:30:00Z",
  "networks": {
    "2g": {
      "technology": "2G-GSM",
      "msc": "MSC-01",
      "active_calls": 5,
      "total_messages": 245
    },
    "3g": {
      "technology": "3G-UMTS",
      "sgsn": "SGSN-01",
      "active_pdp_contexts": 12,
      "total_messages": 458
    },
    "4g": {
      "technology": "4G-LTE",
      "mme": "MME-01",
      "active_bearers": 45,
      "total_messages": 1250,
      "mme_capacity_usage": "0.09%"
    },
    "5g": {
      "technology": "5G-NR",
      "amf": "AMF-01",
      "active_pdu_sessions": 28,
      "total_messages": 892,
      "network_slicing": true
    }
  },
  "total_active_sessions": 90
}
```

### Get Supported Protocols
```bash
curl http://localhost:8080/api/telco/protocols | jq '.'
```

### Subscribe to Telco Signaling (MQTT)
```bash
# Subscribe to all telco protocols
docker exec greengrid-mqtt mosquitto_sub \
  -h localhost \
  -u greengrid \
  -P greengrid123 \
  -t "greengrid/telco/#" \
  -v

# Subscribe to specific protocol
docker exec greengrid-mqtt mosquitto_sub \
  -h localhost \
  -u greengrid \
  -P greengrid123 \
  -t "greengrid/telco/NGAP" \
  -v
```

---

## Integration dengan SCADA

Telco Core Network terintegrasi dengan SCADA untuk monitoring:

```python
# Telco + Energy Metrics
{
  "site_id": "CELL_SITE_001",
  "telco": {
    "2g_calls": 5,
    "3g_sessions": 12,
    "4g_bearers": 45,
    "5g_sessions": 28
  },
  "energy": {
    "power_consumption_kw": 9.8,
    "battery_soc": 75.3,
    "solar_generation_kw": 0.7
  },
  "correlation": {
    "users_vs_power": "positive",
    "efficiency": "optimized"
  }
}
```

---

## Protocol Testing

### Test 2G Call
```python
from telco_core_simulator import GSM_2G_Simulator

sim = GSM_2G_Simulator()
msg = sim.simulate_call_setup()
print(json.dumps(msg, indent=2))
```

### Test 4G Bearer
```python
from telco_core_simulator import LTE_4G_Simulator

sim = LTE_4G_Simulator()
msg = sim.simulate_bearer_setup()
print(json.dumps(msg, indent=2))
```

### Test 5G Slice
```python
from telco_core_simulator import NR_5G_Simulator

sim = NR_5G_Simulator()
msg = sim.simulate_service_request("URLLC")
print(json.dumps(msg, indent=2))
```

---

## Performance Characteristics

### Message Generation Rate
- **2G**: 10% of total traffic (legacy)
- **3G**: 20% of total traffic (declining)
- **4G**: 50% of total traffic (dominant)
- **5G**: 40% of total traffic (growing)

### Peak vs Off-Peak
- **Peak hours** (09:00-17:00): 1-3 seconds interval
- **Off-peak**: 3-7 seconds interval

### Storage
- Signaling messages stored in InfluxDB
- Topic: `greengrid/telco/{protocol}`
- Measurement: `telco_signaling`
- Retention: 30 days default

---

## Standards & Specifications

### 2G/3G (3GPP Release 99)
- TS 29.002 (MAP)
- TS 29.060 (GTP)
- TS 25.413 (RANAP)

### 4G (3GPP Release 8-15)
- TS 36.413 (S1AP)
- TS 29.274 (GTPv2)
- TS 36.423 (X2AP)

### 5G (3GPP Release 15+)
- TS 38.413 (NGAP)
- TS 24.501 (NAS-5G)
- TS 29.244 (PFCP)
- TS 23.501 (5G System Architecture)

---

## Future Enhancements

1. **Real Protocol Decoding**
   - Wireshark/tshark integration
   - Live packet capture
   - Protocol analysis

2. **Advanced Scenarios**
   - Handover simulation
   - Load balancing
   - Failover testing

3. **ML Integration**
   - Traffic prediction
   - Anomaly detection
   - Capacity planning

4. **Multi-vendor Support**
   - Ericsson protocols
   - Huawei protocols
   - Nokia protocols

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-01  
**Standards**: 3GPP Release 15/16/17
