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
RUN pip install google-cloud-bigquery pandas pyarrow numpy
# Copy the rest of the dbt project files to /app
COPY . .

ENV  GOOGLE_APPLICATION_CREDENTIALS="/app/.dbt/cred.json"

# Set permissions for the cred.json file
RUN chmod 600 /app/.dbt/cred.json
ENV DBT_PROFILES_DIR=/app/.dbt

# Set the entry point to run dbt commands
RUN chmod +x Python_Script/main.py

CMD sh -c "if [ -f .dbt/cred.json ]; then \
  echo 'Cred file is present in /app/.dbt'; \
  else echo 'Error: cred.json not found in /app/.dbt'; \
fi; tail -f /dev/null"
