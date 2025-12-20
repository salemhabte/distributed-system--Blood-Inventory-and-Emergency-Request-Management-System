# Blood Bank Authentication System

This distributed system now includes a comprehensive authentication service with role-based access control for blood bank and hospital services.

## Architecture

- **Auth Service**: Central authentication service using MySQL database
- **Blood Bank Service**: SQLite-based service with JWT integration
- **Hospital Service**: PostgreSQL-based service with JWT integration
- **Notification Service**: Kafka-based notification service

## Features

- User registration and login
- JWT authentication with access and refresh tokens
- Role-based access control (blood_bank, hospital, admin)
- Token validation across services
- Secure API endpoints

## Services Overview

### Auth Service (Port 8003)
- **URL**: `http://localhost:8003`
- **Database**: MySQL
- **Endpoints**:
  - `POST /api/auth/register/` - User registration
  - `POST /api/auth/login/` - User login
  - `GET /api/auth/profile/` - User profile
  - `POST /api/auth/change-password/` - Change password
  - `POST /api/auth/logout/` - Logout
  - `GET /api/auth/verify-token/` - Verify token
  - `POST /api/auth/refresh-token/` - Refresh access token

### Blood Bank Service (Port 8001)
- **URL**: `http://localhost:8001`
- **Database**: SQLite
- **Protected Endpoints**:
  - `GET /api/bloodbank/inventory/` - View inventory (all authenticated users)
  - `POST /api/bloodbank/inventory/` - Add blood batch (blood bank & admin only)
  - `POST /api/bloodbank/requests/validate/` - Validate requests (blood bank & admin only)

### Hospital Service (Port 8000)
- **URL**: `http://localhost:8000`
- **Database**: PostgreSQL
- **Protected Endpoints**:
  - `POST /api/hospital/patients` - Create patient (hospital & admin only)
  - `GET /api/hospital/patients/<uuid>` - View patient (all authenticated users)
  - `PUT /api/hospital/patients/<uuid>` - Update patient (hospital & admin only)
  - `GET /api/hospital/blood-requests` - List requests (all authenticated users)
  - `POST /api/hospital/blood-requests` - Create request (hospital & admin only)
  - `GET /api/hospital/inventory` - View inventory (all authenticated users)
  - `PUT /api/hospital/inventory/update` - Update inventory (hospital & admin only)

## User Roles

1. **blood_bank**: Can manage blood inventory and validate requests
2. **hospital**: Can create patients, blood requests, and manage hospital inventory
3. **admin**: Full access to all features

## Getting Started

1. **Start the services**:
   ```bash
   cd Blood_supply
   docker-compose up --build
   ```

   **Default Blood Bank Admin Account:**
   - Username: `bloodbank_admin`
   - Password: `admin123`
   - Role: Blood Bank Admin (automatically created)

2. **Run the demo**:
   ```bash
   python demo_script.py
   ```

   This will demonstrate both blood bank admin and hospital user workflows.

2. **For Hospital Users - Register a new account**:
   ```bash
   curl -X POST http://localhost:8003/api/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{
       "username": "hospital_user",
       "email": "hospital@example.com",
       "password": "password123",
       "password_confirm": "password123",
       "first_name": "Dr. Jane",
       "last_name": "Smith",
       "role": "hospital",
       "organization_name": "City General Hospital",
       "phone_number": "+1234567890",
       "address": "456 Hospital Ave, City, State"
     }'
   ```

3. **Login to get tokens**:
   ```bash
   curl -X POST http://localhost:8003/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{
       "username": "hospital_user",
       "password": "password123"
     }'
   ```

4. **Use access token with protected endpoints**:
   ```bash
   curl -X GET http://localhost:8001/api/bloodbank/inventory/ \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

## API Response Format

### Registration/Login Response
```json
{
  "user": {
    "id": 1,
    "username": "bloodbank_user",
    "email": "bloodbank@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "blood_bank",
    "organization_name": "City Blood Bank",
    "phone_number": "+1234567890",
    "address": "123 Blood St, City, State",
    "is_verified": false,
    "date_joined": "2025-12-20T10:00:00Z",
    "last_login": "2025-12-20T10:00:00Z"
  },
  "tokens": {
    "refresh": "refresh_token_here",
    "access": "access_token_here"
  },
  "message": "User registered successfully"
}
```

## Security Features

- JWT tokens with configurable expiration
- Refresh token rotation
- Token blacklisting on logout
- Role-based permissions
- Password validation
- Secure password hashing

## Environment Variables

### Auth Service
- `MYSQL_DB`: Database name (default: auth_db)
- `MYSQL_USER`: Database user (default: auth_user)
- `MYSQL_PASSWORD`: Database password (default: auth_pass)
- `MYSQL_HOST`: Database host (default: mysql-auth)
- `MYSQL_PORT`: Database port (default: 3306)
- `SECRET_KEY`: Django secret key

### Other Services
- `AUTH_SERVICE_URL`: URL of auth service (default: http://auth-service:8000)

## Database Schema

### Auth Service (MySQL)
- **User table**: Custom user model with role field
- **Token blacklist**: For revoked refresh tokens

### Blood Bank Service (SQLite)
- **Inventory items**: Blood inventory management
- Uses external auth validation

### Hospital Service (PostgreSQL)
- **Patients**: Patient records
- **Blood requests**: Hospital blood requests
- **Hospital inventory**: Hospital blood stock
- Uses external auth validation

## Troubleshooting

1. **Token expired**: Use refresh token to get new access token
2. **Permission denied**: Check user role and endpoint permissions
3. **Service unavailable**: Ensure all services are running with `docker-compose ps`

## Development

To add new permissions or roles:
1. Update the User model in auth service
2. Add corresponding permission classes in individual services
3. Update API documentation

For custom authentication logic, modify the authentication backends in each service.
