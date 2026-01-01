# mqtt-middleware/Dockerfile
FROM python:3.11-slim

# Install Mosquitto MQTT Broker
RUN apt-get update && apt-get install -y \
    mosquitto \
    mosquitto-clients \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Make startup script executable
RUN chmod +x /app/start.sh

# Create Mosquitto config directory
RUN mkdir -p /mosquitto/config /mosquitto/data /mosquitto/log

EXPOSE 1883 9001 4317 4318

CMD ["/app/start.sh"]
