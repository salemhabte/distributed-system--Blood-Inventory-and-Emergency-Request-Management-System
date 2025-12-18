FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run on port 8000 as expected by docker-compose
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]