# Use the official Python image as the base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dbt and other Python dependencies
RUN pip install --upgrade pip
RUN pip install dbt-core
RUN pip install dbt-bigquery

# Copy project files into the container
COPY . /app

# Default command
CMD ["dbt", "--version"]
