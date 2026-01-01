import os
import json
import time
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenTelemetry Configuration
resource = Resource.create({"service.name": "mqtt-middleware"})

# Setup tracing
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Setup metrics
metrics.set_meter_provider(MeterProvider(resource=resource))
meter = metrics.get_meter(__name__)

# Create metrics
message_counter = meter.create_counter(
    name="mqtt_messages_processed",
    description="Number of MQTT messages processed",
    unit="1"
)

latency_histogram = meter.create_histogram(
    name="mqtt_message_latency",
    description="MQTT message processing latency",
    unit="ms"
)

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_USERNAME = os.getenv('MQTT_USERNAME', 'greengrid')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', 'greengrid123')

# Metric filtering rules based on gateway type
METRIC_FILTERS = {
    'CELL': {
        'include': ['voltage', 'current', 'power', 'battery', 'solar', 'temperature', 
                   'signal_strength', 'connected_users'],
        'sample_rate_ms': 5000  # 5 seconds
    },
    'DATACENTER': {
        'include': ['voltage', 'current', 'power', 'temperature', 'humidity', 
                   'cpu_usage', 'memory_usage', 'network_throughput', 'ups_status'],
        'sample_rate_ms': 100  # 100ms for high frequency
    },
    'SWITCHROOM': {
        'include': ['voltage', 'current', 'power', 'temperature', 'humidity',
                   'hvac_status', 'door_status', 'fire_alarm', 'switch_status'],
        'sample_rate_ms': 1000  # 1 second
    }
}

def filter_metrics(data):
    """Filter metrics based on gateway type using OpenTelemetry"""
    with tracer.start_as_current_span("filter_metrics") as span:
        start_time = time.time()
        
        try:
            gateway_type = data.get('gateway_type', 'UNKNOWN')
            raw_metrics = data.get('metrics', {})
            
            span.set_attribute("gateway_type", gateway_type)
            span.set_attribute("raw_metric_count", len(raw_metrics))
            
            # Get filter rules for this gateway type
            filter_rules = METRIC_FILTERS.get(gateway_type, {})
            include_list = filter_rules.get('include', [])
            
            # Filter metrics
            filtered_metrics = {}
            for metric_name, metric_value in raw_metrics.items():
                if any(included in metric_name.lower() for included in include_list):
                    filtered_metrics[metric_name] = metric_value
            
            data['metrics'] = filtered_metrics
            data['filtered_at'] = datetime.utcnow().isoformat()
            data['sample_rate_ms'] = filter_rules.get('sample_rate_ms', 1000)
            
            span.set_attribute("filtered_metric_count", len(filtered_metrics))
            
            # Record metrics
            message_counter.add(1, {"gateway_type": gateway_type, "status": "filtered"})
            
            latency = (time.time() - start_time) * 1000
            latency_histogram.record(latency, {"operation": "filter"})
            
            logger.info(f"Filtered {len(raw_metrics)} -> {len(filtered_metrics)} metrics for {gateway_type}")
            
            return data
            
        except Exception as e:
            span.record_exception(e)
            logger.error(f"Error filtering metrics: {e}")
            return data

def on_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        logger.info("Connected to MQTT broker")
        # Subscribe to all edge gateway raw topics
        client.subscribe("greengrid/edge/+/raw")
    else:
        logger.error(f"Failed to connect: {rc}")

def on_message(client, userdata, msg):
    """Process incoming MQTT messages"""
    with tracer.start_as_current_span("process_mqtt_message") as span:
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            span.set_attribute("topic", topic)
            span.set_attribute("gateway_id", payload.get('gateway_id', 'unknown'))
            
            # Filter metrics based on gateway type
            filtered_data = filter_metrics(payload)
            
            # Publish filtered data to processed topic
            gateway_id = filtered_data.get('gateway_id', 'unknown')
            processed_topic = f"greengrid/edge/{gateway_id}/metrics"
            
            client.publish(
                processed_topic, 
                json.dumps(filtered_data),
                qos=1
            )
            
            logger.info(f"Published filtered data to {processed_topic}")
            
        except Exception as e:
            span.record_exception(e)
            logger.error(f"Error processing message: {e}")

def main():
    """Main function"""
    logger.info("Starting OpenTelemetry MQTT Processor...")
    
    # Wait for Mosquitto to start
    time.sleep(5)
    
    # Create MQTT client
    client = mqtt.Client(client_id="otel_processor")
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        logger.info("MQTT client connected, starting loop...")
        client.loop_forever()
    except Exception as e:
        logger.error(f"Error in MQTT loop: {e}")
        time.sleep(5)
        main()  # Retry connection

if __name__ == "__main__":
    main()
