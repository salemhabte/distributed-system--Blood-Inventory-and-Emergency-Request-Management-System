#!/bin/bash

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
python -c "
import time
import socket
import os

host = os.getenv('MYSQL_HOST', 'mysql-auth')
port = int(os.getenv('MYSQL_PORT', 3306))

while True:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print('MySQL is ready!')
            break
        else:
            print('MySQL is unavailable - sleeping')
            time.sleep(2)
    except Exception as e:
        print(f'Error checking MySQL: {e}')
        time.sleep(2)
"

echo "MySQL is up - creating and executing migrations"
python manage.py makemigrations
python manage.py migrate

echo "Creating default admin user"
python manage.py create_default_admin

echo "Collecting static files"
python manage.py collectstatic --noinput --clear

echo "Starting Django server"
exec python manage.py runserver 0.0.0.0:8000
