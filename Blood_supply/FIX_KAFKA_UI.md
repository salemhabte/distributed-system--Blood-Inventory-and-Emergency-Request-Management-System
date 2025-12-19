# Fix Kafka UI (Kafdrop) and Import Errors

## Issues Fixed:
1. ✅ Missing imports in `views.py` - Added kafka_events imports
2. ✅ Kafka UI (Kafdrop) not accessible - Updated docker-compose.yml

## Commands to Fix and Restart:

### 1. Stop All Running Containers
```bash
cd Blood_supply
docker-compose down
```

### 2. Rebuild Hospital Service (to pick up import fixes)
```bash
docker-compose build hospital-service
```

### 3. Start All Services
```bash
docker-compose up -d
```

### 4. Check if Kafdrop is Running
```bash
docker-compose ps kafdrop
docker-compose logs kafdrop
```

### 5. Access Kafka UI
Open your browser and go to: **http://localhost:9000**

If it's still not working, check the logs:
```bash
docker-compose logs kafdrop
```

### 6. Restart Kafdrop if Needed
```bash
docker-compose restart kafdrop
```

### 7. Run Migrations (Important!)
```bash
docker-compose exec hospital-service python manage.py makemigrations
docker-compose exec hospital-service python manage.py migrate
```

## Verify Everything is Working:

### Test Hospital Service API:
```bash
# Test patient creation (this should now work)
curl -X POST http://localhost:8000/api/v1/hospital/patients/ \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "age": 30,
    "bloodType": "O+",
    "diagnosis": "Test"
  }'
```

### Check Kafka UI:
- Open: http://localhost:9000
- You should see the Kafdrop interface
- Topics should appear as events are published

### Check Service Logs:
```bash
# Hospital service logs
docker-compose logs -f hospital-service

# Kafka logs
docker-compose logs -f kafka

# Kafdrop logs
docker-compose logs -f kafdrop
```

## Troubleshooting Kafdrop:

If Kafdrop UI still doesn't load:

### Option 1: Check if port 9000 is in use
```bash
# Windows PowerShell
netstat -ano | findstr :9000

# If something is using it, stop it or change the port in docker-compose.yml
```

### Option 2: Try alternative Kafdrop image
If the current image doesn't work, you can try:
```yaml
# In docker-compose.yml, replace kafdrop service with:
kafdrop:
  image: provectuslabs/kafdrop:latest
  restart: unless-stopped
  environment:
    KAFKA_BROKERCONNECT: kafka:29092
  ports:
    - "9000:9000"
  depends_on:
    - kafka
```

### Option 3: Manual Kafdrop Start
```bash
docker run -d --rm \
  --name kafdrop \
  --network blood_supply_default \
  -p 9000:9000 \
  -e KAFKA_BROKERCONNECT=kafka:29092 \
  obsidiandynamics/kafdrop
```

## All Services Status Check:
```bash
docker-compose ps
```

All services should show as "Up" or "running".
