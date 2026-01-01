import os
import json
import time
import random
import threading
import logging
from datetime import datetime
from flask import Flask, jsonify
import paho.mqtt.client as mqtt
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
GATEWAY_ID = os.getenv('GATEWAY_ID', 'CELL_SITE_001')
GATEWAY_TYPE = 'CELL'
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mqtt-middleware:1883').split(':')[0]
MQTT_PORT = 1883
MQTT_USERNAME = os.getenv('MQTT_USERNAME', 'greengrid')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', 'greengrid123')
LOCATION_LAT = float(os.getenv('LOCATION_LAT', '-6.2088'))
LOCATION_LON = float(os.getenv('LOCATION_LON', '106.8456'))
BUFFER_SIZE = int(os.getenv('OFFLINE_BUFFER_SIZE', '10000'))

# Flask app for local API
app = Flask(__name__)

# Global state
mqtt_client = None
is_connected = False
offline_buffer = deque(maxlen=BUFFER_SIZE)

# Simulated device states
device_states = {
    'energy_meter': {
        'voltage_l1': 220.0,
        'voltage_l2': 220.0,
        'voltage_l3': 220.0,
        'current_l1': 15.0,
        'current_l2': 14.5,
        'current_l3': 15.2,
        'power_total_kw': 9.8,
        'energy_total_kwh': 1250.5,
        'power_factor': 0.95,
        'frequency': 50.0
    },
    'battery_bms': {
        'voltage': 48.2,
        'current': -12.5,
        'soc_percent': 75.3,
        'soh_percent': 98.5,
        'temperature': 28.5,
        'charging_status': 'discharging',
        'cycles': 450,
        'capacity_ah': 200.0
    },
    'solar_mppt': {
        'pv_voltage': 85.5,
        'pv_current': 8.2,
        'pv_power_kw': 0.7,
        'battery_voltage': 48.2,
        'battery_current': 12.0,
        'daily_energy_kwh': 5.8,
        'total_energy_kwh': 3250.0,
        'mppt_efficiency': 98.2
    },
    'genset_control': {
        'status': 'standby',
        'voltage': 0.0,
        'current': 0.0,
        'power_kw': 0.0,
        'frequency': 0.0,
        'fuel_level_percent': 85.0,
        'runtime_hours': 1250,
        'temperature': 35.0
    },
    'telco_equipment': {
        '2g_status': 'active',
        '3g_status': 'active',
        '4g_status': 'active',
        '5g_status': 'active',
        'signal_strength_dbm': -65.0,
        'connected_users': 145,
        'data_throughput_mbps': 125.5,
        'equipment_temp': 42.0
    },
    'end_user_meter': {
        'active_users': 12,
        'total_consumption_kwh': 45.2,
        'avg_power_kw': 3.5,
        'peak_power_kw': 5.8,
        'power_quality': 'good'
    }
}

def generate_realistic_metrics():
    """Generate realistic sensor data with variations"""
    
    # Add realistic variations
    hour = datetime.now().hour
    
    # Solar generation varies by time of day
    if 6 <= hour <= 18:
        solar_factor = random.uniform(0.8, 1.0) if 10 <= hour <= 15 else random.uniform(0.3, 0.6)
    else:
        solar_factor = 0.0
    
    device_states['solar_mppt']['pv_voltage'] = 85.5 + random.uniform(-2, 2)
    device_states['solar_mppt']['pv_current'] = 8.2 * solar_factor + random.uniform(-0.5, 0.5)
    device_states['solar_mppt']['pv_power_kw'] = round(
        device_states['solar_mppt']['pv_voltage'] * device_states['solar_mppt']['pv_current'] / 1000, 2
    )
    
    # Energy meter variations
    base_load = 9.8
    load_variation = random.uniform(-1.5, 1.5)
    device_states['energy_meter']['power_total_kw'] = base_load + load_variation
    device_states['energy_meter']['current_l1'] = (base_load + load_variation) / 0.66
    device_states['energy_meter']['voltage_l1'] = 220.0 + random.uniform(-5, 5)
    
    # Battery state
    device_states['battery_bms']['soc_percent'] = max(20, min(100, 
        device_states['battery_bms']['soc_percent'] + random.uniform(-0.5, 0.5)))
    device_states['battery_bms']['voltage'] = 42.0 + (device_states['battery_bms']['soc_percent'] / 100) * 10
    device_states['battery_bms']['temperature'] = 28.5 + random.uniform(-2, 3)
    
    # Telco equipment
    device_states['telco_equipment']['connected_users'] = int(145 + random.uniform(-20, 20))
    device_states['telco_equipment']['data_throughput_mbps'] = 125.5 + random.uniform(-15, 15)
    device_states['telco_equipment']['signal_strength_dbm'] = -65.0 + random.uniform(-5, 5)
    device_states['telco_equipment']['equipment_temp'] = 42.0 + random.uniform(-3, 5)
    
    # End user consumption
    device_states['end_user_meter']['active_users'] = int(12 + random.uniform(-2, 3))
    device_states['end_user_meter']['avg_power_kw'] = 3.5 + random.uniform(-0.5, 1.0)
    
    # Compile all metrics
    metrics = {}
    for device, values in device_states.items():
        for key, value in values.items():
            metric_name = f"{device}_{key}"
            metrics[metric_name] = value
    
    return metrics

def on_mqtt_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    global is_connected
    if rc == 0:
        logger.info(f"Connected to MQTT broker - {GATEWAY_ID}")
        is_connected = True
        
        # Send buffered messages
        send_buffered_messages()
        
        # Publish status
        status_message = {
            'gateway_id': GATEWAY_ID,
            'gateway_type': GATEWAY_TYPE,
            'status': 'online',
            'location': {'lat': LOCATION_LAT, 'lon': LOCATION_LON},
            'timestamp': datetime.utcnow().isoformat()
        }
        client.publish(f"greengrid/edge/{GATEWAY_ID}/status", json.dumps(status_message), qos=1)
    else:
        logger.error(f"Failed to connect to MQTT broker: {rc}")
        is_connected = False

def on_mqtt_disconnect(client, userdata, rc):
    """MQTT disconnection callback"""
    global is_connected
    is_connected = False
    logger.warning(f"Disconnected from MQTT broker - {GATEWAY_ID}")

def send_buffered_messages():
    """Send buffered messages when connection is restored"""
    global offline_buffer
    if offline_buffer:
        logger.info(f"Sending {len(offline_buffer)} buffered messages")
        while offline_buffer:
            try:
                msg = offline_buffer.popleft()
                mqtt_client.publish(msg['topic'], msg['payload'], qos=1)
            except Exception as e:
                logger.error(f"Error sending buffered message: {e}")

def publish_metrics():
    """Publish metrics to MQTT broker"""
    while True:
        try:
            metrics = generate_realistic_metrics()
            
            message = {
                'gateway_id': GATEWAY_ID,
                'gateway_type': GATEWAY_TYPE,
                'location': {'lat': LOCATION_LAT, 'lon': LOCATION_LON},
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': metrics
            }
            
            payload = json.dumps(message)
            topic = f"greengrid/edge/{GATEWAY_ID}/raw"
            
            if is_connected:
                result = mqtt_client.publish(topic, payload, qos=1)
                if result.rc != 0:
                    logger.warning("Failed to publish, buffering message")
                    offline_buffer.append({'topic': topic, 'payload': payload})
            else:
                # Buffer message for later
                offline_buffer.append({'topic': topic, 'payload': payload})
                logger.info(f"Offline mode: buffered message ({len(offline_buffer)}/{BUFFER_SIZE})")
            
            time.sleep(5)  # Cell site reports every 5 seconds
            
        except Exception as e:
            logger.error(f"Error publishing metrics: {e}")
            time.sleep(5)

def init_mqtt():
    """Initialize MQTT client"""
    global mqtt_client
    
    mqtt_client = mqtt.Client(client_id=GATEWAY_ID)
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_disconnect = on_mqtt_disconnect
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        is_connected = False

# Flask API endpoints
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'gateway_id': GATEWAY_ID,
        'status': 'online',
        'mqtt_connected': is_connected,
        'buffer_size': len(offline_buffer),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/metrics', methods=['GET'])
def get_current_metrics():
    return jsonify({
        'gateway_id': GATEWAY_ID,
        'metrics': device_states,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/control/genset/<action>', methods=['POST'])
def control_genset(action):
    """Control genset (start/stop)"""
    if action in ['start', 'stop']:
        device_states['genset_control']['status'] = 'running' if action == 'start' else 'standby'
        return jsonify({'status': 'success', 'action': action})
    return jsonify({'status': 'error', 'message': 'Invalid action'}), 400

def main():
    """Main function"""
    logger.info(f"Starting Edge Gateway CELL - {GATEWAY_ID}")
    
    # Initialize MQTT
    init_mqtt()
    
    # Start metrics publisher thread
    metrics_thread = threading.Thread(target=publish_metrics, daemon=True)
    metrics_thread.start()
    
    # Start Flask API
    app.run(host='0.0.0.0', port=8081, debug=False)

if __name__ == '__main__':
    main()
