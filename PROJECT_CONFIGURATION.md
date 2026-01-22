# Project Configuration & Dependencies Guide

## 📋 Table of Contents
1. [Project Architecture Overview](#project-architecture-overview)
2. [Service Configuration Details](#service-configuration-details)
3. [Complete Dependency List](#complete-dependency-list)
4. [Docker Configuration](#docker-configuration)
5. [Database Configuration](#database-configuration)
6. [Kafka Event-Driven Architecture](#kafka-event-driven-architecture)
7. [Authentication Flow](#authentication-flow)
8. [Network & Port Configuration](#network--port-configuration)



## 🏗️ Project Architecture Overview

This is a **distributed microservices system** for Blood Inventory and Emergency Request Management with:

- **4 Backend Microservices** (Django REST Framework)
- **1 Frontend Application** (React + Vite)
- **Event-Driven Communication** (Apache Kafka)
- **Polyglot Persistence** (MySQL, PostgreSQL, SQLite)
- **Containerized Deployment** (Docker Compose)

---

## 🔧 Service Configuration Details

### 1. **Auth Service** (Port 8003)

**Purpose**: Centralized authentication and authorization

**Configuration** (`auth_service/settings.py`):
- **Database**: MySQL 8.0
- **Authentication**: JWT (JSON Web Tokens)
- **User Model**: Custom (`authentication.User`)
- **Token Lifetime**: 
  - Access Token: 15 minutes
  - Refresh Token: 7 days
- **Token Rotation**: Enabled with blacklisting

**Key Settings**:
```python
AUTH_USER_MODEL = 'authentication.User'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
```

**Environment Variables**:
- `MYSQL_DB=auth_db`
- `MYSQL_USER=auth_user`
- `MYSQL_PASSWORD=auth_pass`
- `MYSQL_HOST=mysql-auth`
- `MYSQL_PORT=3306`
- `DJANGO_DEBUG=True`

**Entrypoint Script** (`entrypoint.sh`):
- Waits for MySQL to be ready
- Runs database migrations
- Creates default admin user
- Collects static files
- Starts Django server

---

### 2. **Hospital Service** (Port 8000)

**Purpose**: Hospital operations (patient management, blood requests)

**Configuration** (`hospital_service/settings.py`):
- **Database**: PostgreSQL 15
- **Authentication**: Validates JWT tokens from Auth Service
- **Kafka Integration**: Publishes blood request events

**Key Settings**:
```python
AUTH_SERVICE_URL = 'http://auth-service:8000'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'hospital_app.authentication.LocalJWTAuthentication',
    ),
}
```

**Environment Variables**:
- `KAFKA_BOOTSTRAP_SERVERS=kafka:29092`
- `POSTGRES_DB=hospital_db`
- `POSTGRES_USER=hospital_user`
- `POSTGRES_PASSWORD=hospital_pass`
- `POSTGRES_HOST=postgres-hospital`
- `POSTGRES_PORT=5432`

**Kafka Topics Used**:
- `blood-requests`: Publishes when blood requests are created

---

### 3. **Blood Bank Service** (Port 8001)

**Purpose**: Blood inventory management

**Configuration** (`bloodbank_service/settings.py`):
- **Database**: SQLite (file-based)
- **Authentication**: Validates JWT tokens from Auth Service
- **Kafka Integration**: Both producer and consumer

**Key Settings**:
```python
AUTH_SERVICE_URL = 'http://auth-service:8000'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Environment Variables**:
- `KAFKA_BOOTSTRAP_SERVERS=kafka:29092`

**Kafka Topics Used**:
- Consumes: `blood-requests` (validates and processes requests)
- Publishes: Inventory update events

---

### 4. **Notification Service** (Port 8002)

**Purpose**: Event-driven notifications

**Configuration** (`notification_service/settings.py`):
- **Database**: SQLite
- **Kafka Integration**: Consumer only

**Environment Variables**:
- `KAFKA_BOOTSTRAP_SERVERS=kafka:29092`

**Kafka Topics Consumed**:
- `blood-requests`: Listens for new blood requests
- `inventory-updates`: Listens for inventory changes
- `low-stock-alerts`: Listens for low stock warnings

---

### 5. **Frontend** (Port 3000)

**Purpose**: React-based user interface

**Configuration** (`frontend/vite.config.js`):
```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true  // Allows external access
  }
})
```

**API Endpoints** (`frontend/src/services/api.js`):
- Auth Service: `http://localhost:8003/api/auth`
- Hospital Service: `http://localhost:8000/api/v1/hospital`
- Blood Bank Service: `http://localhost:8001/api/v1/blood-bank`

**Axios Interceptor**: Automatically adds JWT token to all requests

---

## 📦 Complete Dependency List

### **Backend Dependencies (Python)**

#### **Auth Service** (`auth_service/requirements.txt`)
```txt
Django==5.0.7                          # Web framework
djangorestframework==3.15.1            # REST API framework
djangorestframework-simplejwt==5.3.0   # JWT authentication
django-environ==0.11.2                 # Environment variable management
mysqlclient==2.2.4                      # MySQL database adapter
PyJWT==2.8.0                           # JWT token encoding/decoding
python-dateutil==2.8.2                 # Date/time utilities
django-cors-headers==4.4.0             # CORS handling
```

**Purpose of Each**:
- **Django**: Core web framework
- **djangorestframework**: REST API capabilities
- **djangorestframework-simplejwt**: JWT token generation/validation
- **django-environ**: Loads config from environment variables
- **mysqlclient**: Connects to MySQL database
- **PyJWT**: Low-level JWT operations
- **python-dateutil**: Date parsing/formatting
- **django-cors-headers**: Allows cross-origin requests from frontend

---

#### **Hospital Service** (`hospital_service/requirements.txt`)
```txt
Django==5.0.7                          # Web framework
djangorestframework==3.15.1            # REST API framework
djangorestframework-simplejwt==5.3.0   # JWT token validation
kafka-python==2.0.2                    # Kafka producer/consumer
psycopg2-binary==2.9.9                  # PostgreSQL database adapter
django-environ==0.11.2                 # Environment variable management
requests==2.31.0                        # HTTP client (for auth service calls)
```

**Purpose of Each**:
- **Django**: Core web framework
- **djangorestframework**: REST API capabilities
- **djangorestframework-simplejwt**: Validates JWT tokens
- **kafka-python**: Publishes events to Kafka
- **psycopg2-binary**: Connects to PostgreSQL database
- **django-environ**: Environment configuration
- **requests**: Makes HTTP calls to auth service for token validation

---

#### **Blood Bank Service** (`bloodbank_service/requirements.txt`)
```txt
Django==5.0.7                          # Web framework
djangorestframework==3.15.1            # REST API framework
djangorestframework-simplejwt==5.3.0   # JWT token validation
kafka-python==2.0.2                    # Kafka producer/consumer
django-environ==0.11.2                 # Environment variable management
python-dateutil==2.8.2                 # Date/time utilities
requests==2.31.0                        # HTTP client
```

**Purpose of Each**:
- **Django**: Core web framework
- **djangorestframework**: REST API capabilities
- **djangorestframework-simplejwt**: Validates JWT tokens
- **kafka-python**: Both produces and consumes Kafka events
- **django-environ**: Environment configuration
- **python-dateutil**: Date utilities
- **requests**: HTTP client for inter-service communication

---

#### **Notification Service** (`notification_service/requirements.txt`)
```txt
Django                              # Web framework (version not pinned)
djangorestframework                 # REST API framework
kafka-python                        # Kafka consumer
```

**Purpose of Each**:
- **Django**: Core web framework
- **djangorestframework**: REST API for notification endpoints
- **kafka-python**: Consumes events from Kafka topics

---

### **Frontend Dependencies** (`frontend/package.json`)

#### **Production Dependencies**
```json
{
  "axios": "^1.7.2",                    // HTTP client for API calls
  "framer-motion": "^11.2.10",          // Animation library
  "lucide-react": "^0.395.0",           // Icon library
  "react": "^18.3.1",                   // UI framework
  "react-dom": "^18.3.1",               // React DOM renderer
  "react-router-dom": "^6.23.1"         // Client-side routing
}
```

**Purpose of Each**:
- **axios**: Makes HTTP requests to backend APIs
- **framer-motion**: Smooth animations and transitions
- **lucide-react**: Modern icon components
- **react**: Core UI library
- **react-dom**: React rendering for web
- **react-router-dom**: Navigation and routing

#### **Development Dependencies**
```json
{
  "@types/react": "^18.3.3",            // TypeScript types for React
  "@types/react-dom": "^18.3.0",        // TypeScript types for React DOM
  "@vitejs/plugin-react": "^4.3.1",     // Vite plugin for React
  "eslint": "^8.57.0",                  // Code linting
  "eslint-plugin-react": "^7.34.2",     // React-specific ESLint rules
  "eslint-plugin-react-hooks": "^4.6.2", // React Hooks linting
  "eslint-plugin-react-refresh": "^0.4.7", // React Fast Refresh linting
  "vite": "^5.3.1"                      // Build tool and dev server
}
```

**Purpose of Each**:
- **@types/react**: TypeScript definitions
- **@vitejs/plugin-react**: Enables React in Vite
- **eslint**: Code quality and style checking
- **eslint-plugin-react**: React-specific linting rules
- **eslint-plugin-react-hooks**: Validates React Hooks usage
- **vite**: Fast build tool and development server

---

### **Infrastructure Dependencies** (Docker Images)

#### **From docker-compose.yml**:
```yaml
mysql:8.0                              # MySQL database for auth service
postgres:15                            # PostgreSQL database for hospital service
confluentinc/cp-zookeeper:7.6.0       # Zookeeper for Kafka coordination
wurstmeister/kafka:latest              # Apache Kafka message broker
obsidiandynamics/kafdrop              # Kafka web UI
python:3.11-slim                       # Python base image for services
python:3.14-slim                       # Python base image (notification service)
```

---

## 🐳 Docker Configuration

### **Docker Compose Services**

#### **1. Database Services**

**MySQL (Auth Service)**:
```yaml
mysql-auth:
  image: mysql:8.0
  ports: "3307:3306"  # Host:Container
  environment:
    MYSQL_ROOT_PASSWORD: root_password
    MYSQL_DATABASE: auth_db
    MYSQL_USER: auth_user
    MYSQL_PASSWORD: auth_pass
  volumes:
    - mysql_auth_data:/var/lib/mysql
  command: --default-authentication-plugin=mysql_native_password
```

**PostgreSQL (Hospital Service)**:
```yaml
postgres-hospital:
  image: postgres:15
  ports: "5433:5432"  # Host:Container
  environment:
    POSTGRES_DB: hospital_db
    POSTGRES_USER: hospital_user
    POSTGRES_PASSWORD: hospital_pass
  volumes:
    - postgres_hospital_data:/var/lib/postgresql/data
```

#### **2. Message Broker Services**

**Zookeeper**:
```yaml
zookeeper:
  image: confluentinc/cp-zookeeper:7.6.0
  ports: "2181:2181"
  environment:
    ZOOKEEPER_CLIENT_PORT: 2181
    ZOOKEEPER_TICK_TIME: 2000
```

**Kafka**:
```yaml
kafka:
  image: wurstmeister/kafka:latest
  ports:
    - "9092:9092"    # External access
  environment:
    KAFKA_BROKER_ID: 1
    KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    KAFKA_LISTENERS: INTERNAL://0.0.0.0:29092,EXTERNAL://0.0.0.0:9092
    KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka:29092,EXTERNAL://localhost:9092
    KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
```

**Kafdrop** (Kafka UI):
```yaml
kafdrop:
  image: obsidiandynamics/kafdrop
  ports: "9000:9000"
  environment:
    KAFKA_BROKERCONNECT: "kafka:29092"
```

#### **3. Application Services**

All services follow similar Dockerfile pattern:

**Base Configuration**:
- Python 3.11-slim (or 3.14-slim for notification)
- Working directory: `/app`
- Environment: `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`
- Exposed port: `8000`

**Auth Service Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
# Installs MySQL client libraries
RUN apt-get update && apt-get install -y gcc default-libmysqlclient-dev pkg-config
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
USER app  # Non-root user
ENTRYPOINT ["/entrypoint.sh"]
```

---

## 🗄️ Database Configuration

### **Polyglot Persistence Strategy**

| Service | Database | Reason |
|---------|----------|--------|
| Auth Service | MySQL 8.0 | Relational data, user management, token blacklisting |
| Hospital Service | PostgreSQL 15 | Complex relational queries, ACID compliance |
| Blood Bank Service | SQLite | Lightweight, embedded, simple inventory |
| Notification Service | SQLite | Simple event storage, low overhead |

### **Connection Configuration**

**MySQL (Auth)**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('MYSQL_DB'),
        'USER': env('MYSQL_USER'),
        'PASSWORD': env('MYSQL_PASSWORD'),
        'HOST': env('MYSQL_HOST'),  # 'mysql-auth' in Docker
        'PORT': env('MYSQL_PORT'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 60,  # Connection pooling
    }
}
```

**PostgreSQL (Hospital)**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),  # 'postgres-hospital' in Docker
        'PORT': env('POSTGRES_PORT'),
        'CONN_MAX_AGE': 60,
    }
}
```

**SQLite (Blood Bank & Notification)**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

---

## 📨 Kafka Event-Driven Architecture

### **Kafka Configuration**

**Bootstrap Servers**: `kafka:29092` (internal Docker network)

**Topics Used**:
1. **`blood-requests`**: Blood request events
   - **Publisher**: Hospital Service
   - **Consumers**: Blood Bank Service, Notification Service
   
2. **`inventory-updates`**: Inventory change events
   - **Publisher**: Blood Bank Service
   - **Consumers**: Notification Service

3. **`low-stock-alerts`**: Low stock warnings
   - **Publisher**: Blood Bank Service
   - **Consumers**: Notification Service

### **Kafka Producer Configuration**

```python
KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    retries=5,
    acks='all'  # Wait for all replicas
)
```

### **Kafka Consumer Configuration**

```python
KafkaConsumer(
    *topics,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="notification-service-group"
)
```

### **Event Flow Example**

1. **Hospital creates blood request** → Publishes to `blood-requests` topic
2. **Blood Bank Service** consumes event → Validates inventory
3. **Notification Service** consumes event → Sends notifications
4. **Blood Bank updates inventory** → Publishes to `inventory-updates`
5. **Notification Service** consumes update → Sends confirmation

---

## 🔐 Authentication Flow

### **JWT Token Flow**

1. **User Login** (Frontend → Auth Service):
   ```
   POST /api/auth/login/
   → Returns: { access_token, refresh_token }
   ```

2. **Token Storage** (Frontend):
   ```javascript
   localStorage.setItem('access_token', token)
   ```

3. **API Request** (Frontend → Any Service):
   ```javascript
   headers: { Authorization: 'Bearer <access_token>' }
   ```

4. **Token Validation** (Service → Auth Service):
   - Option 1: Local validation (if same SECRET_KEY)
   - Option 2: HTTP call to auth service

5. **Token Refresh** (Frontend → Auth Service):
   ```
   POST /api/auth/token/refresh/
   → Returns: { access_token }
   ```

### **JWT Configuration**

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

---

## 🌐 Network & Port Configuration

### **Port Mapping**

| Service | Host Port | Container Port | Access URL |
|---------|-----------|----------------|------------|
| Auth Service | 8003 | 8000 | http://localhost:8003 |
| Hospital Service | 8000 | 8000 | http://localhost:8000 |
| Blood Bank Service | 8001 | 8000 | http://localhost:8001 |
| Notification Service | 8002 | 8000 | http://localhost:8002 |
| Frontend | 3000 | 3000 | http://localhost:3000 |
| MySQL | 3307 | 3306 | localhost:3307 |
| PostgreSQL | 5433 | 5432 | localhost:5433 |
| Kafka | 9092 | 9092 | localhost:9092 |
| Kafdrop | 9000 | 9000 | http://localhost:9000 |
| Zookeeper | 2181 | 2181 | localhost:2181 |

### **Docker Network**

All services communicate via Docker's default bridge network:
- **Service-to-Service**: Use service names (e.g., `http://auth-service:8000`)
- **Host-to-Service**: Use `localhost:<host_port>`
- **Kafka Internal**: `kafka:29092`
- **Kafka External**: `localhost:9092`

---

## 🚀 Startup Sequence

1. **Infrastructure** starts first:
   - MySQL, PostgreSQL
   - Zookeeper, Kafka

2. **Auth Service** starts:
   - Waits for MySQL
   - Runs migrations
   - Creates admin user

3. **Other Services** start:
   - Wait for Kafka
   - Wait for their databases
   - Run migrations

4. **Frontend** runs separately:
   - `npm run dev` (Vite dev server)
   - Connects to backend services

---

## 📝 Environment Variables Summary

### **Auth Service**
- `MYSQL_DB`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`
- `DJANGO_DEBUG`, `SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`

### **Hospital Service**
- `KAFKA_BOOTSTRAP_SERVERS`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `DJANGO_DEBUG`, `SECRET_KEY`

### **Blood Bank Service**
- `KAFKA_BOOTSTRAP_SERVERS`

### **Notification Service**
- `KAFKA_BOOTSTRAP_SERVERS`

---

## 🔄 Data Flow Example

**Complete Request Flow**:

1. **User logs in** → Frontend → Auth Service → Returns JWT
2. **User creates blood request** → Frontend → Hospital Service (with JWT)
3. **Hospital Service validates JWT** → Auth Service
4. **Hospital Service creates request** → Saves to PostgreSQL
5. **Hospital Service publishes event** → Kafka topic `blood-requests`
6. **Blood Bank Service consumes** → Validates inventory → Updates SQLite
7. **Notification Service consumes** → Creates notification → Saves to SQLite
8. **Blood Bank publishes update** → Kafka topic `inventory-updates`
9. **Notification Service consumes** → Sends notification to user

---

## 🛠️ Development Setup

1. **Start Backend Services**:
   ```bash
   cd Blood_supply
   docker-compose up -d
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access Services**:
   - Frontend: http://localhost:3000
   - Auth API: http://localhost:8003
   - Hospital API: http://localhost:8000
   - Blood Bank API: http://localhost:8001
   - Notification API: http://localhost:8002
   - Kafka UI: http://localhost:9000

---

## 📚 Key Technologies Summary

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| Backend Framework | Django | 5.0.7 | Web framework |
| API Framework | Django REST Framework | 3.15.1 | REST APIs |
| Authentication | JWT (Simple JWT) | 5.3.0 | Token-based auth |
| Message Broker | Apache Kafka | Latest | Event streaming |
| Frontend Framework | React | 18.3.1 | UI library |
| Build Tool | Vite | 5.3.1 | Dev server & bundler |
| HTTP Client | Axios | 1.7.2 | API requests |
| Database | MySQL, PostgreSQL, SQLite | Various | Data persistence |
| Containerization | Docker | - | Service isolation |
| Orchestration | Docker Compose | - | Multi-container management |

---

This configuration enables a scalable, maintainable, and loosely-coupled distributed system architecture.

