# edge-gateway-cell/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create buffer directory
RUN mkdir -p /data/buffer

# Make startup script executable
RUN chmod +x /app/start.sh

EXPOSE 5020 8081

CMD ["/app/start.sh"]
