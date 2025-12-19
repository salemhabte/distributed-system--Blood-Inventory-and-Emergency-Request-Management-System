# Fix Kafka Networking Issue for Kafdrop

## Problem
Kafdrop cannot resolve the hostname "kafka" - getting `UnknownHostException: kafka`

## Solution
All services need to be on the same Docker network. Updated docker-compose.yml to use a shared `kafka-network`.

## Commands to Fix:

### 1. Stop All Containers
```bash
cd Blood_supply
docker-compose down
```

### 2. Remove Old Networks (Optional but recommended)
```bash
docker network prune -f
```

### 3. Start All Services Again
```bash
docker-compose up -d --build
```

### 4. Wait for Kafka to be Ready (10-15 seconds)
```bash
# Check Kafka logs to see when it's ready
docker-compose logs -f kafka
# Wait until you see "started" messages, then Ctrl+C
```

### 5. Check Kafdrop Logs
```bash
docker-compose logs kafdrop
```

### 6. Verify Kafdrop Can Resolve Kafka
```bash
# Test from inside Kafdrop container
docker-compose exec kafdrop ping kafka
```

### 7. Access Kafka UI
Open browser: **http://localhost:9000**

## Alternative: If Still Not Working

### Option 1: Use provectuslabs/kafdrop image
Replace the kafdrop service in docker-compose.yml:
```yaml
kafdrop:
  image: provectuslabs/kafdrop:latest
  restart: unless-stopped
  container_name: kafdrop
  environment:
    KAFKA_BROKERCONNECT: kafka:29092
    SERVER_PORT: 9000
  ports:
    - "9000:9000"
  depends_on:
    - kafka
  networks:
    - kafka-network
```

### Option 2: Check Network Connectivity
```bash
# List all networks
docker network ls

# Inspect the network
docker network inspect blood_supply_kafka-network

# Check if all containers are connected
docker network inspect blood_supply_kafka-network | grep -A 5 Containers
```

### Option 3: Manual Test
```bash
# Start a test container on the same network
docker run --rm --network blood_supply_kafka-network \
  alpine ping -c 3 kafka

# If this works, the network is fine and it's a Kafdrop-specific issue
```

## Verification Commands

```bash
# Check all services are running
docker-compose ps

# Check network connectivity from hospital-service
docker-compose exec hospital-service ping -c 3 kafka

# Check Kafdrop logs for connection success
docker-compose logs kafdrop | grep -i "connected\|ready\|started"
```
