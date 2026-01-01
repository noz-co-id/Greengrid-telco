#!/bin/bash
# edge-gateway-cell/start.sh
set -e

echo "Starting Edge Gateway CELL - ${GATEWAY_ID}"

# Wait for MQTT broker to be ready
echo "Waiting for MQTT broker..."
until nc -z ${MQTT_BROKER} 1883; do
    echo "MQTT broker is unavailable - sleeping"
    sleep 2
done
echo "MQTT broker is up - starting application"

# Start the main application
python /app/main.py

# ============================================

#!/bin/bash
# edge-gateway-datacenter/start.sh
set -e

echo "Starting Edge Gateway DATACENTER - ${GATEWAY_ID}"

# Wait for MQTT broker to be ready
echo "Waiting for MQTT broker..."
until nc -z ${MQTT_BROKER} 1883; do
    echo "MQTT broker is unavailable - sleeping"
    sleep 2
done
echo "MQTT broker is up - starting application"

# Start the main application
python /app/main.py

# ============================================

#!/bin/bash
# edge-gateway-switchroom/start.sh
set -e

echo "Starting Edge Gateway SWITCHROOM - ${GATEWAY_ID}"

# Wait for MQTT broker to be ready
echo "Waiting for MQTT broker..."
until nc -z ${MQTT_BROKER} 1883; do
    echo "MQTT broker is unavailable - sleeping"
    sleep 2
done
echo "MQTT broker is up - starting application"

# Start the main application
python /app/main.py
