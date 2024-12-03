# Base image (choose Python-based image to support dbt)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

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

# Set the entry point to run dbt commands
CMD ["dbt"]
