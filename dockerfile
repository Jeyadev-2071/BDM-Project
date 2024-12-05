FROM python:3.11-slim
# Set working directory
WORKDIR /app

# Install system dependencies, including git
RUN apt-get update && apt-get install -y \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN ls -la
# Copy the dbt project files to /app
COPY . .
# Install dbt-bigquery and other Python dependencies
RUN  pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install "apache-airflow[celery]==2.10.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.3/constraints-3.11.txt"
RUN pip install --upgrade dbt-core dbt-bigquery dbt-postgres
# Set environment variables
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/.dbt/cred.json"
ENV DBT_PROFILES_DIR=/app/.dbt

# Create a non-root user to run the container
RUN useradd -ms /bin/bash airflow && \
    chown -R airflow:airflow /app

# Switch to the non-root user
USER airflow

# Verify if the credentials file exists
CMD sh -c "if [ -f /app/.dbt/cred.json ]; then \
  echo 'Cred file is present in /app/.dbt'; \
  else echo 'Error: cred.json not found in /app/.dbt'; \
fi; tail -f /dev/null"