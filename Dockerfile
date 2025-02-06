FROM openjdk:8-jdk-slim

# Install essential tools
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg2 \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3 and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*


# Install PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client

# Install Procps (for process monitoring)
RUN apt-get update && apt-get install -y procps

# Create Spark jars directory
RUN mkdir -p /opt/spark/jars

# Download PostgreSQL JDBC driver for Spark
RUN wget https://jdbc.postgresql.org/download/postgresql-42.2.24.jar -O /opt/spark/jars/postgresql-42.2.24.jar

# Copy data.csv to the /app directory
COPY data.csv /app/data.csv

# Install required Python dependencies
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

# Copy environment variables and ETL script
COPY .env /app/.env
COPY etl_script.py /app/etl_script.py

# Run the ETL Python script and SQL queries
ENTRYPOINT ["sh", "-c", "python3 /app/etl_script.py && PGPASSWORD=$(cat /run/secrets/postgres_password) psql -h db -U worker -d testdatabase -f /app/queries.sql"]
