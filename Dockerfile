# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Ensure logs directory exists
RUN mkdir -p logs

# Define environment variable for config
ENV CONFIG_FILE=config/config.ini

# Run the scheduler
CMD ["python", "scheduler/scheduler.py"]
