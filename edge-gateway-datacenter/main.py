import os
import json
import time
import random
import threading
import logging
from datetime import datetime
from flask import Flask, jsonify
import paho.mqtt.client as mqtt
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
GATEWAY_ID = os.getenv('GATEWAY_ID', 'DC_SITE_001')
GATEWAY_TYPE = 'DATACENTER'
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mqtt-middleware:1883').split(':')[0]
MQTT_PORT = 1883
MQTT_USERNAME = os.getenv('MQTT_USERNAME', 'greengrid')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', 'greengrid123')
LOCATION_LAT = float(os.getenv('LOCATION_LAT', '-6.2293'))
LOCATION_LON = float(os.getenv('LOCATION_LON', '106.8467'))
SAMPLING_RATE_MS = int(os.getenv('SAMPLING_RATE_MS', '100'))

# Flask app
app = Flask(__name__)

# Global state
mqtt_client = None
is_connected = False

# Data Center Equipment States
device_states = {
    'ups_systems': {
        'ups_1': {
            'status': 'online',
            'load_percent': 65.5,
            'input_voltage': 220.0,
            'output_voltage': 220.0,
            'input_frequency': 50.0,
            'output_frequency': 50.0,
            'battery_voltage': 240.0,
            'battery_current': 0.0,
            'battery_soc_percent': 100.0,
            'battery_temp': 25.0,
            'estimated_runtime_min': 45,
            'alarms': []
        },
        'ups_2': {
            'status': 'online',
            'load_percent': 68.2,
            'input_voltage': 220.0,
            'output_voltage': 220.0,
            'battery_soc_percent': 100.0,
            'estimated_runtime_min': 42
        }
    },
    'cooling_systems': {
        'crac_1': {
            'status': 'running',
            'supply_temp_c': 18.5,
            'return_temp_c': 28.2,
            'humidity_percent': 45.0,
            'fan_speed_percent': 75.0,
            'compressor_status': 'on',
            'power_kw': 12.5,
            'alarms': []
        },
        'crac_2': {
            'status': 'running',
            'supply_temp_c': 18.8,
            'return_temp_c': 28.5,
            'humidity_percent': 46.0,
            'fan_speed_percent': 72.0,
            'compressor_status': 'on',
            'power_kw': 12.2
        }
    },
    'servers': {
        'rack_1': {
            'total_servers': 42,
            'active_servers': 42,
            'cpu_avg_percent': 45.5,
            'memory_avg_percent': 68.2,
            'disk_avg_percent': 55.0,
            'inlet_temp_c': 22.5,
            'power_kw': 15.8,
            'network_rx_gbps': 2.5,
            'network_tx_gbps': 1.8
        },
        'rack_2': {
            'total_servers': 42,
            'active_servers': 40,
            'cpu_avg_percent': 52.3,
            'memory_avg_percent': 71.5,
            'disk_avg_percent': 62.0,
            'inlet_temp_c': 23.1,
            'power_kw': 16.2,
            'network_rx_gbps': 3.1,
            'network_tx_gbps': 2.3
        }
    },
    'network_switches': {
        'core_switch_1': {
            'status': 'active',
            'uptime_hours': 8520,
            'cpu_percent': 25.5,
            'memory_percent': 42.0,
            'temperature_c': 45.0,
            'port_utilization_percent': 65.0,
            'total_ports': 48,
            'active_ports': 42,
            'throughput_gbps': 15.5,
            'packet_loss_percent': 0.01,
            'errors': 0
        },
        'core_switch_2': {
            'status': 'active',
            'uptime_hours': 8520,
            'cpu_percent': 28.2,
            'memory_percent': 45.5,
            'temperature_c': 46.5,
            'port_utilization_percent': 68.0,
            'total_ports': 48,
            'active_ports': 44,
            'throughput_gbps': 17.2,
            'packet_loss_percent': 0.02
        }
    },
    'power_distribution': {
        'pdu_1': {
            'voltage_l1': 220.0,
            'voltage_l2': 220.0,
            'voltage_l3': 220.0,
            'current_l1': 85.5,
            'current_l2': 87.2,
            'current_l3': 84.8,
            'power_total_kw': 56.5,
            'energy_kwh': 125600.0,
            'power_factor': 0.98
        },
        'pdu_2': {
            'voltage_l1': 220.0,
            'voltage_l2': 220.0,
            'voltage_l3': 220.0,
            'current_l1': 82.3,
            'current_l2': 83.5,
            'current_l3': 81.9,
            'power_total_kw': 54.2,
            'energy_kwh': 118900.0,
            'power_factor': 0.97
        }
    },
    'environmental': {
        'hot_aisle_temp_c': 32.5,
        'cold_aisle_temp_c': 20.5,
        'ambient_humidity_percent': 45.0,
        'differential_pressure_pa': 15.0,
        'smoke_detector': 'normal',
        'water_leak_detector': 'normal'
    },
    'pue_metrics': {
        'pue': 1.45,
        'it_power_kw': 110.7,
        'total_facility_power_kw': 160.5,
        'cooling_power_kw': 24.7,
        'lighting_power_kw': 5.1,
        'other_power_kw': 20.0
    }
}

def generate_high_freq_metrics():
    """Generate high-frequency metrics (100ms sampling)"""
    
    # Simulate realistic variations
    # UPS load fluctuations
    device_states['ups_systems']['ups_1']['load_percent'] += random.uniform(-0.5, 0.5)
    device_states['ups_systems']['ups_1']['load_percent'] = max(60, min(70, 
        device_states['ups_systems']['ups_1']['load_percent']))
    
    device_states['ups_systems']['ups_1']['input_voltage'] = 220.0 + random.uniform(-2, 2)
    device_states['ups_systems']['ups_1']['output_voltage'] = 220.0 + random.uniform(-0.5, 0.5)
    
    # Cooling system variations
    device_states['cooling_systems']['crac_1']['supply_temp_c'] = 18.5 + random.uniform(-0.5, 0.5)
    device_states['cooling_systems']['crac_1']['return_temp_c'] = 28.2 + random.uniform(-1, 1)
    device_states['cooling_systems']['crac_1']['humidity_percent'] = 45.0 + random.uniform(-2, 2)
    
    # Server metrics
    device_states['servers']['rack_1']['cpu_avg_percent'] += random.uniform(-2, 2)
    device_states['servers']['rack_1']['cpu_avg_percent'] = max(40, min(90, 
        device_states['servers']['rack_1']['cpu_avg_percent']))
    
    device_states['servers']['rack_1']['memory_avg_percent'] += random.uniform(-1, 1)
    device_states['servers']['rack_1']['memory_avg_percent'] = max(60, min(80, 
        device_states['servers']['rack_1']['memory_avg_percent']))
    
    device_states['servers']['rack_1']['inlet_temp_c'] = 22.5 + random.uniform(-0.5, 1.0)
    device_states['servers']['rack_1']['network_rx_gbps'] = 2.5 + random.uniform(-0.3, 0.5)
    device_states['servers']['rack_1']['network_tx_gbps'] = 1.8 + random.uniform(-0.2, 0.4)
    
    # Network switch metrics
    device_states['network_switches']['core_switch_1']['cpu_percent'] = 25.5 + random.uniform(-2, 5)
    device_states['network_switches']['core_switch_1']['temperature_c'] = 45.0 + random.uniform(-1, 2)
    device_states['network_switches']['core_switch_1']['throughput_gbps'] = 15.5 + random.uniform(-2, 3)
    
    # Power distribution
    device_states['power_distribution']['pdu_1']['current_l1'] = 85.5 + random.uniform(-3, 3)
    device_states['power_distribution']['pdu_1']['power_total_kw'] = (
        device_states['power_distribution']['pdu_1']['current_l1'] * 0.66
    )
    
    # Environmental
    device_states['environmental']['hot_aisle_temp_c'] = 32.5 + random.uniform(-1, 2)
    device_states['environmental']['cold_aisle_temp_c'] = 20.5 + random.uniform(-0.5, 0.5)
    
    # PUE calculation
    it_power = (device_states['power_distribution']['pdu_1']['power_total_kw'] + 
                device_states['power_distribution']['pdu_2']['power_total_kw'])
    cooling_power = (device_states['cooling_systems']['crac_1']['power_kw'] + 
                     device_states['cooling_systems']['crac_2']['power_kw'])
    total_power = it_power + cooling_power + 25.1  # lighting + other
    
    device_states['pue_metrics']['it_power_kw'] = it_power
    device_states['pue_metrics']['total_facility_power_kw'] = total_power
    device_states['pue_metrics']['cooling_power_kw'] = cooling_power
    device_states['pue_metrics']['pue'] = round(total_power / it_power, 3) if it_power > 0 else 1.0
    
    # Compile all metrics
    metrics = {}
    for category, data in device_states.items():
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, (int, float)):
                            metric_name = f"{category}_{key}_{subkey}"
                            metrics[metric_name] = subvalue
                elif isinstance(value, (int, float, str)):
                    metric_name = f"{category}_{key}"
                    metrics[metric_name] = value
    
    return metrics

def on_mqtt_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    global is_connected
    if rc == 0:
        logger.info(f"Connected to MQTT broker - {GATEWAY_ID}")
        is_connected = True
        
        # Publish status
        status_message = {
            'gateway_id': GATEWAY_ID,
            'gateway_type': GATEWAY_TYPE,
            'status': 'online',
            'location': {'lat': LOCATION_LAT, 'lon': LOCATION_LON},
            'high_frequency': True,
            'sampling_rate_ms': SAMPLING_RATE_MS,
            'timestamp': datetime.utcnow().isoformat()
        }
        client.publish(f"greengrid/edge/{GATEWAY_ID}/status", json.dumps(status_message), qos=1)
    else:
        logger.error(f"Failed to connect to MQTT broker: {rc}")
        is_connected = False

def publish_metrics():
    """Publish high-frequency metrics"""
    while True:
        try:
            if is_connected:
                metrics = generate_high_freq_metrics()
                
                message = {
                    'gateway_id': GATEWAY_ID,
                    'gateway_type': GATEWAY_TYPE,
                    'location': {'lat': LOCATION_LAT, 'lon': LOCATION_LON},
                    'timestamp': datetime.utcnow().isoformat(),
                    'metrics': metrics
                }
                
                payload = json.dumps(message)
                topic = f"greengrid/edge/{GATEWAY_ID}/raw"
                
                mqtt_client.publish(topic, payload, qos=0)  # QoS 0 for high frequency
            
            time.sleep(SAMPLING_RATE_MS / 1000.0)  # Convert ms to seconds
            
        except Exception as e:
            logger.error(f"Error publishing metrics: {e}")
            time.sleep(1)

def init_mqtt():
    """Initialize MQTT client"""
    global mqtt_client
    
    mqtt_client = mqtt.Client(client_id=GATEWAY_ID)
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_connect = on_mqtt_connect
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")

# Flask API endpoints
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'gateway_id': GATEWAY_ID,
        'status': 'online',
        'mqtt_connected': is_connected,
        'sampling_rate_ms': SAMPLING_RATE_MS,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/metrics', methods=['GET'])
def get_current_metrics():
    return jsonify({
        'gateway_id': GATEWAY_ID,
        'metrics': device_states,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/pue', methods=['GET'])
def get_pue():
    return jsonify(device_states['pue_metrics'])

def main():
    """Main function"""
    logger.info(f"Starting Edge Gateway DATACENTER - {GATEWAY_ID}")
    
    # Initialize MQTT
    init_mqtt()
    
    # Start high-frequency metrics publisher
    metrics_thread = threading.Thread(target=publish_metrics, daemon=True)
    metrics_thread.start()
    
    # Start Flask API
    app.run(host='0.0.0.0', port=8082, debug=False)

if __name__ == '__main__':
    main()
