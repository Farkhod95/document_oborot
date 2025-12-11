# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# System-level deps (agar kerak bo'lsa, psycopg2 va boshqalar uchun)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

# wait-for-it.sh ni executable qilamiz
RUN chmod +x /app/wait-for-it.sh

# Expose the required port (container ichida)
EXPOSE 8000

# Default command (docker-compose override qiladi baribir)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "main.asgi:application"]
