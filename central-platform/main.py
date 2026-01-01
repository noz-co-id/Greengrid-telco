import os
import json
import time
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import psycopg2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# InfluxDB Configuration
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "admin:admin123"
INFLUX_ORG = "greengrid"
INFLUX_BUCKET = "telco_metrics"

# PostgreSQL Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres123'),
    'database': os.getenv('POSTGRES_DB', 'geospatial_db')
}

# MQTT Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mqtt-middleware:1883').split(':')[0]
MQTT_PORT = 1883

# Global clients
influx_client = None
write_api = None
mqtt_client = None

def init_influxdb():
    """Initialize InfluxDB client"""
    global influx_client, write_api
    try:
        influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        logger.info("InfluxDB client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize InfluxDB: {e}")

def on_mqtt_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        logger.info("Connected to MQTT broker")
        # Subscribe to all edge gateway topics
        client.subscribe("greengrid/edge/+/metrics")
        client.subscribe("greengrid/edge/+/status")
        client.subscribe("greengrid/edge/+/alerts")
    else:
        logger.error(f"Failed to connect to MQTT broker: {rc}")

def on_mqtt_message(client, userdata, msg):
    """MQTT message callback"""
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        
        logger.info(f"Received message on topic: {topic}")
        
        # Process metrics data
        if "/metrics" in topic:
            process_metrics(payload)
        elif "/status" in topic:
            process_status(payload)
        elif "/alerts" in topic:
            process_alerts(payload)
            
    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}")

def process_metrics(data):
    """Process and store metrics in InfluxDB"""
    try:
        gateway_id = data.get('gateway_id')
        gateway_type = data.get('gateway_type')
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        metrics = data.get('metrics', {})
        
        # Write to InfluxDB
        for metric_name, metric_value in metrics.items():
            point = Point("telco_metrics") \
                .tag("gateway_id", gateway_id) \
                .tag("gateway_type", gateway_type) \
                .field(metric_name, float(metric_value)) \
                .time(timestamp)
            
            write_api.write(bucket=INFLUX_BUCKET, record=point)
        
        logger.info(f"Stored metrics from {gateway_id}")
        
    except Exception as e:
        logger.error(f"Error processing metrics: {e}")

def process_status(data):
    """Process gateway status updates"""
    logger.info(f"Gateway status update: {data}")

def process_alerts(data):
    """Process gateway alerts"""
    logger.warning(f"Gateway alert: {data}")

def init_mqtt():
    """Initialize MQTT client"""
    global mqtt_client
    try:
        mqtt_client = mqtt.Client(client_id="central_platform")
        mqtt_client.on_connect = on_mqtt_connect
        mqtt_client.on_message = on_mqtt_message
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        logger.info("MQTT client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MQTT: {e}")

# REST API Endpoints

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'influxdb': influx_client is not None,
            'mqtt': mqtt_client is not None and mqtt_client.is_connected()
        }
    })

@app.route('/api/sites', methods=['GET'])
def get_sites():
    """Get all sites with geospatial data"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT site_id, site_name, site_type, 
                   ST_X(location::geometry) as longitude,
                   ST_Y(location::geometry) as latitude,
                   address, province, city, capacity_kw, status
            FROM sites;
        """)
        
        sites = []
        for row in cursor.fetchall():
            sites.append({
                'site_id': row[0],
                'site_name': row[1],
                'site_type': row[2],
                'longitude': float(row[3]),
                'latitude': float(row[4]),
                'address': row[5],
                'province': row[6],
                'city': row[7],
                'capacity_kw': float(row[8]) if row[8] else 0,
                'status': row[9]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'sites': sites})
        
    except Exception as e:
        logger.error(f"Error fetching sites: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/realtime', methods=['GET'])
def get_realtime_metrics():
    """Get real-time metrics from InfluxDB"""
    try:
        gateway_id = request.args.get('gateway_id')
        
        query = f'''
            from(bucket: "{INFLUX_BUCKET}")
            |> range(start: -1h)
            |> filter(fn: (r) => r._measurement == "telco_metrics")
        '''
        
        if gateway_id:
            query += f'|> filter(fn: (r) => r.gateway_id == "{gateway_id}")'
        
        query_api = influx_client.query_api()
        result = query_api.query(query)
        
        metrics = []
        for table in result:
            for record in table.records:
                metrics.append({
                    'gateway_id': record.values.get('gateway_id'),
                    'gateway_type': record.values.get('gateway_type'),
                    'metric': record.get_field(),
                    'value': record.get_value(),
                    'timestamp': record.get_time().isoformat()
                })
        
        return jsonify({'metrics': metrics})
        
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/esg/report', methods=['GET'])
def get_esg_report():
    """Generate ESG/SDG report"""
    try:
        # Calculate ESG metrics from database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Sample ESG data
        esg_data = {
            'report_date': datetime.utcnow().date().isoformat(),
            'environmental': {
                'total_energy_consumption_mwh': 1250.5,
                'renewable_energy_percentage': 35.2,
                'carbon_emissions_tons': 450.3,
                'water_usage_m3': 12500,
                'waste_recycled_percentage': 68.5
            },
            'social': {
                'total_sites': 3,
                'communities_served': 15000,
                'jobs_created': 45,
                'local_procurement_percentage': 72.3
            },
            'governance': {
                'compliance_rate': 98.5,
                'safety_incidents': 2,
                'training_hours': 1250
            },
            'sdg_alignment': {
                'SDG7': 'Affordable and Clean Energy - 35% renewable',
                'SDG9': 'Industry, Innovation and Infrastructure - Network expansion',
                'SDG11': 'Sustainable Cities - Urban connectivity',
                'SDG13': 'Climate Action - Carbon reduction initiatives'
            }
        }
        
        cursor.close()
        conn.close()
        
        return jsonify(esg_data)
        
    except Exception as e:
        logger.error(f"Error generating ESG report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """Get dashboard summary data"""
    try:
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_sites': 3,
            'active_gateways': 3,
            'total_power_kw': 650.0,
            'renewable_percentage': 35.2,
            'network_uptime': 99.8,
            'alerts': {
                'critical': 0,
                'warning': 2,
                'info': 5
            }
        }
        
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {e}")
        return jsonify({'error': str(e)}), 500

def main():
    """Main application entry point"""
    logger.info("Starting Central Platform...")
    
    # Wait for services to be ready
    time.sleep(10)
    
    # Initialize connections
    init_influxdb()
    init_mqtt()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    main()
