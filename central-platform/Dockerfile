# central-platform/Dockerfile
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    wget \
    gnupg \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Telco Core Network Simulators (Open Source)
# Install srsRAN (4G/5G software radio)
RUN apt-get update && apt-get install -y \
    cmake \
    libfftw3-dev \
    libmbedtls-dev \
    libboost-program-options-dev \
    libconfig++-dev \
    libsctp-dev \
    libuhd-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Open5GS (5G Core Network)
RUN wget https://open5gs.org/open5gs/assets/webui/install -O /tmp/open5gs-install.sh && \
    chmod +x /tmp/open5gs-install.sh

# Install Osmocom (2G/3G Core Network)
RUN apt-get update && apt-get install -y \
    libosmocore-dev \
    libosmo-netif-dev \
    libosmo-abis-dev \
    libosmo-sccp-dev \
    osmo-bts \
    osmo-bsc \
    osmo-msc \
    osmo-hlr \
    osmo-sgsn \
    osmo-ggsn \
    && rm -rf /var/lib/apt/lists/*

# Install InfluxDB
RUN wget -q https://repos.influxdata.com/influxdata-archive_compat.key && \
    echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && \
    cat influxdata-archive_compat.key | gpg --dearmor | tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null && \
    echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | tee /etc/apt/sources.list.d/influxdata.list && \
    apt-get update && apt-get install -y influxdb && \
    rm -rf /var/lib/apt/lists/*

# Install PostgreSQL with PostGIS
RUN apt-get update && apt-get install -y \
    postgresql \
    postgresql-contrib \
    postgis \
    && rm -rf /var/lib/apt/lists/*

# Install Grafana
RUN wget -q -O /usr/share/keyrings/grafana.key https://apt.grafana.com/gpg.key && \
    echo "deb [signed-by=/usr/share/keyrings/grafana.key] https://apt.grafana.com stable main" | tee -a /etc/apt/sources.list.d/grafana.list && \
    apt-get update && apt-get install -y grafana && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Make startup script executable
RUN chmod +x /app/start.sh

EXPOSE 8086 5432 3000 8080

CMD ["/app/start.sh"]
