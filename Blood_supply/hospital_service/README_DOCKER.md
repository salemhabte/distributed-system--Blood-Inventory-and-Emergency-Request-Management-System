# Docker Commands for Hospital Service

## Quick Start

### 1. Build and Start All Services
```bash
# Navigate to Blood_supply directory
cd Blood_supply

# Build and start all services (Kafka, Zookeeper, Hospital, Bloodbank, Notification)
docker-compose up --build
```

### 2. Run in Detached Mode (Background)
```bash
docker-compose up -d --build
```

### 3. View Logs
```bash
# All services
docker-compose logs -f

# Hospital service only
docker-compose logs -f hospital-service

# Follow logs for specific service
docker-compose logs -f hospital-service bloodbank-service
```

## Hospital Service Specific Commands

### Run Migrations
```bash
# Run migrations in the hospital-service container
docker-compose exec hospital-service python manage.py makemigrations
docker-compose exec hospital-service python manage.py migrate
```

### Create Superuser (for Django Admin)
```bash
docker-compose exec hospital-service python manage.py createsuperuser
```

### Run Kafka Consumer (in a separate container or terminal)
```bash
# Option 1: Run in existing container (new terminal/tab)
docker-compose exec hospital-service python manage.py run_consumer

# Option 2: Run in a separate container
docker-compose run --rm hospital-service python manage.py run_consumer
```

### Access Django Shell
```bash
docker-compose exec hospital-service python manage.py shell
```

### Access Container Shell
```bash
docker-compose exec hospital-service bash
```

## Individual Service Management

### Start Only Hospital Service
```bash
# Make sure Kafka is running first
docker-compose up kafka zookeeper -d
docker-compose up hospital-service
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

### Restart Hospital Service
```bash
docker-compose restart hospital-service
```

### Rebuild Hospital Service Only
```bash
docker-compose build hospital-service
docker-compose up hospital-service
```

## Development Workflow

### 1. First Time Setup
```bash
# Build all services
docker-compose build

# Start infrastructure (Kafka, Zookeeper)
docker-compose up -d kafka zookeeper

# Wait for Kafka to be ready (about 10-15 seconds)
sleep 15

# Run migrations
docker-compose exec hospital-service python manage.py makemigrations
docker-compose exec hospital-service python manage.py migrate

# Start hospital service
docker-compose up hospital-service
```

### 2. Running Multiple Terminals for Full System

**Terminal 1: Infrastructure & Services**
```bash
docker-compose up
```

**Terminal 2: Hospital Kafka Consumer**
```bash
docker-compose exec hospital-service python manage.py run_consumer
```

**Terminal 3: Bloodbank Kafka Consumer (if needed)**
```bash
docker-compose exec bloodbank-service python manage.py run_consumer
```

## Health Checks & Debugging

### Check if Services are Running
```bash
docker-compose ps
```

### Check Hospital Service Logs
```bash
docker-compose logs hospital-service
```

### Inspect Container
```bash
docker-compose exec hospital-service bash
# Inside container:
# - Check environment variables: env | grep KAFKA
# - Check if Kafka is reachable: python -c "from kafka import KafkaProducer; print(KafkaProducer(bootstrap_servers='kafka:9092'))"
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/api/v1/hospital/

# List patients
curl http://localhost:8000/api/v1/hospital/patients/

# List blood requests
curl http://localhost:8000/api/v1/hospital/blood-requests/
```

## Kafka Management

### Access Kafdrop UI (Kafka Web UI)
Open browser: http://localhost:9000

### List Kafka Topics (inside container)
```bash
docker-compose exec hospital-service python -c "
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
admin = KafkaAdminClient(bootstrap_servers='kafka:9092')
print(admin.list_topics())
"
```

## Troubleshooting

### If Hospital Service Can't Connect to Kafka
```bash
# Check if Kafka is running
docker-compose ps kafka

# Check Kafka logs
docker-compose logs kafka

# Verify network connectivity
docker-compose exec hospital-service ping kafka
```

### Reset Everything
```bash
# Stop all services and remove volumes
docker-compose down -v

# Remove images (optional)
docker-compose rm -f

# Rebuild and start fresh
docker-compose up --build
```

### View Container Environment
```bash
docker-compose exec hospital-service env
```

## Production-like Setup (Recommended)

Create a startup script or use docker-compose override for production:

```bash
# Run migrations on startup (if needed)
docker-compose exec hospital-service python manage.py migrate

# Start the service
docker-compose up hospital-service
```

## Service URLs

- **Hospital Service API**: http://localhost:8000/api/v1/hospital/
- **Hospital Admin**: http://localhost:8000/admin/
- **Bloodbank Service**: http://localhost:8001/
- **Notification Service**: http://localhost:8002/
- **Kafdrop (Kafka UI)**: http://localhost:9000

## Notes

- The hospital service runs on port **8000** (mapped from container port 8000)
- Kafka bootstrap servers are configured via `KAFKA_BOOTSTRAP_SERVERS=kafka:9092` environment variable
- Database (SQLite) is stored in the container at `/app/db.sqlite3`
- Use `docker-compose exec` to run commands in running containers
- Use `docker-compose run --rm` to run commands in new temporary containers
