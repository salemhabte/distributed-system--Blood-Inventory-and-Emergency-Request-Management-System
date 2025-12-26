FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Copy and make entrypoint executable
# Fix Windows line endings (CRLF -> LF) and make executable
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Note: Migrations and admin creation will be run at container startup
# This allows MySQL to be available when the container starts

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

# Expose port
EXPOSE 8000

# Run as root to execute entrypoint, entrypoint will handle user switching if needed
ENTRYPOINT ["/entrypoint.sh"]

