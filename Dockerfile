# Use official Python 3.10 base image
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy your project files
COPY . .

# Expose port
EXPOSE 8000

# Start the server with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:vj"]
