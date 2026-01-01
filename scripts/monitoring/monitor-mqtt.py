#!/usr/bin/env python3
# monitor-mqtt.py
# Real-time MQTT monitoring dashboard

import paho.mqtt.client as mqtt
import json
from datetime import datetime
import sys

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_USERNAME = "greengrid"
MQTT_PASSWORD = "greengrid123"

# Statistics
stats = {
    'CELL_SITE_001': {'count': 0, 'last_update': None},
    'DC_SITE_001': {'count': 0, 'last_update': None},
    'SR_SITE_001': {'count': 0, 'last_update': None}
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✓ Connected to MQTT broker")
        print("=" * 80)
        print("Monitoring MQTT traffic... (Press Ctrl+C to stop)")
        print("=" * 80)
        
        # Subscribe to all topics
        client.subscribe("greengrid/#")
    else:
        print(f"✗ Connection failed with code {rc}")
        sys.exit(1)

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        
        # Update statistics
        gateway_id = payload.get('gateway_id', 'UNKNOWN')
        if gateway_id in stats:
            stats[gateway_id]['count'] += 1
            stats[gateway_id]['last_update'] = datetime.now().strftime('%H:%M:%S')
        
        # Display message info
        gateway_type = payload.get('gateway_type', 'UNKNOWN')
        timestamp = payload.get('timestamp', 'N/A')
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {topic}")
        print(f"  Gateway: {gateway_id} ({gateway_type})")
        print(f"  Timestamp: {timestamp}")
        
        # Display key metrics based on gateway type
        metrics = payload.get('metrics', {})
        
        if gateway_type == 'CELL':
            print(f"  Power: {metrics.get('energy_meter_power_total_kw', 0):.2f} kW")
            print(f"  Battery SOC: {metrics.get('battery_bms_soc_percent', 0):.1f}%")
            print(f"  Solar Power: {metrics.get('solar_mppt_pv_power_kw', 0):.2f} kW")
            print(f"  Connected Users: {metrics.get('telco_equipment_connected_users', 0)}")
            
        elif gateway_type == 'DATACENTER':
            print(f"  IT Power: {metrics.get('pue_metrics_it_power_kw', 0):.2f} kW")
            print(f"  PUE: {metrics.get('pue_metrics_pue', 0):.3f}")
            print(f"  UPS 1 Load: {metrics.get('ups_systems_ups_1_load_percent', 0):.1f}%")
            print(f"  Cooling Power: {metrics.get('cooling_systems_crac_1_power_kw', 0):.2f} kW")
            
        elif gateway_type == 'SWITCHROOM':
            print(f"  Power: {metrics.get('power_distribution_main_breaker_power_total_kw', 0):.2f} kW")
            print(f"  Room Temp: {metrics.get('environmental_sensors_room_temp_c', 0):.1f}°C")
            print(f"  HVAC Power: {metrics.get('hvac_control_hvac_1_power_kw', 0):.2f} kW")
            print(f"  Generator: {metrics.get('generators_genset_main_status', 'N/A')}")
        
        # Show statistics
        print(f"\n  Statistics:")
        for gw_id, data in stats.items():
            if data['count'] > 0:
                print(f"    {gw_id}: {data['count']} messages | Last: {data['last_update']}")
        
        print("-" * 80)
        
    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    client = mqtt.Client(client_id="mqtt_monitor")
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        print("Connecting to MQTT broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\nStopping monitor...")
        print("\nFinal Statistics:")
        print("=" * 80)
        for gw_id, data in stats.items():
            print(f"{gw_id}: {data['count']} total messages")
        print("=" * 80)
        client.disconnect()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
