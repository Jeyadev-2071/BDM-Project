# Base image (choose Python-based image to support dbt)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies, including git
RUN apt-get update && apt-get install -y \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# Install dbt-bigquery
RUN pip install dbt-bigquery

# Copy the rest of the dbt project files to /app
COPY . .

# Add an ARG to accept the service account key
ARG GCP_SERVICE_ACCOUNT_KEY

# Write the service account key to /app/.dbt/cred.json
RUN echo "$GCP_SERVICE_ACCOUNT_KEY" > /app/.dbt/cred.json

# Set permissions for the cred.json file
RUN chmod 600 /app/.dbt/cred.json
ENV DBT_PROFILES_DIR=/app/.dbt
# Set the entry point to run dbt commands
CMD sh -c "if [ -f /app/.dbt/cred.json ]; then \
  echo 'Cred file is present in /app/.dbt'; \
  else echo 'Error: cred.json not found in /app/.dbt'; \
fi; tail -f /dev/null"