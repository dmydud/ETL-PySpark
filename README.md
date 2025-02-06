# Data Engineering Task: ETL Pipeline with Docker

This project involves building an ETL pipeline that extracts data from a CSV file, performs transformations, loads it into a PostgreSQL database, and runs SQL queries. The entire process is containerized using Docker.

## Project Structure

```
.
├── etl_script.py                        # Python script for the ETL process
├── generate_user_data.py                # Python script to generate fake user data
├── Dockerfile                           # Dockerfile for building the Python app container
├── docker-compose.yml                   # Docker Compose configuration
├── requirements.txt                     # Python dependencies
├── .env                                  # Environment variables for PostgreSQL
├── secrets/                             # Directory for Docker secrets
│   └── postgres_password                # Docker secret containing PostgreSQL password
├── sql/                                  # Directory for SQL queries and PostgreSQL setup
│   ├── create_table.sql                 # SQL script to create PostgreSQL table
│   └── queries.sql                      # SQL queries to interact with the database
└── README.md                            # Project documentation
```

## Assumptions

- The CSV file contains 1000+ records with columns: `user_id`, `name`, `email`, and `signup_date`.
- The `signup_date` field is in timestamp format and needs to be standardized.
- Only valid email addresses will be processed, and any invalid email will be removed.
- A new column `domain` will be added to store the email domain (e.g., `gmail.com`, `example.com`).
- PostgreSQL will be used as the database for storing transformed data.
- Docker containers will be used for both the Python application and PostgreSQL database.

## Prerequisites

Make sure you have the following installed:

- Docker
- Docker Compose
- Python 3.x (for development)


## Example `.env`

The `.env` file contains environment variables for PostgreSQL and Docker secrets configuration. Here’s an example:

```
JDBC_URL=jdbc:postgresql://db:5432/testdatabase
POSTGRES_USER=worker
POSTGRES_TABLE=users
POSTGRES_DB=testdatabase
SECRET_POSTGRES_PASSWORD_PATH=./secrets/postgres_password
```

This file ensures that the correct PostgreSQL connection parameters are used by the Python application when connecting to the database. The `SECRET_POSTGRES_PASSWORD_PATH` variable indicates the location of the Docker secret that contains the PostgreSQL password.

## Instructions

### 1. **Build and Run the Docker Containers**

To build and run the Docker containers, follow these steps:

1. **Build the Docker containers**:
   ```
   docker-compose build
   ```

2. **Run the Docker containers**:
   ```
   docker-compose up
   ```

   This will start the Python application container and the PostgreSQL container. The Python application will run the ETL process, extract data from the CSV, transform it, and load it into the PostgreSQL database.

### 2. **Accessing the PostgreSQL Database**

Once the containers are running, you can connect to the PostgreSQL database via the following command:

```
docker exec -it <postgres_container_name> psql -U postgres
```

The PostgreSQL database will be running inside the container with the default `postgres` user. You can run SQL queries against the database using the command line or a database client.

### 3. **Running SQL Queries**

The required SQL queries are located in the `sql/queries.sql` file. You can execute these queries manually using the following commands inside the PostgreSQL container:

1. **Retrieve the count of users who signed up on each day**:
   ```sql
   SELECT signup_date, COUNT(*) FROM users GROUP BY signup_date;
   ```

2. **List all unique email domains**:
   ```sql
   SELECT DISTINCT domain FROM users;
   ```

3. **Retrieve the details of users whose signup date is within the last 7 days**:
   ```sql
   SELECT * FROM users WHERE signup_date > CURRENT_DATE - INTERVAL '7 days';
   ```

4. **Find the user(s) with the most common email domain**:
   ```sql
   SELECT domain, COUNT(*) FROM users GROUP BY domain ORDER BY COUNT(*) DESC LIMIT 1;
   ```

5. **Delete records where the email domain is not in a specific list**:
   ```sql
   DELETE FROM users WHERE domain NOT IN ('gmail.com', 'yahoo.com', 'example.com');
   ```

### 4. **Database Schema**

The PostgreSQL table `users` will be created based on the following schema:

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    signup_date DATE,
    domain VARCHAR(255)
);
```

### 5. **Verify the Results**

You can verify the results of the ETL process by checking the contents of the `users` table in the PostgreSQL database after running the pipeline:

- Ensure the `signup_date` is correctly transformed to the `YYYY-MM-DD` format.
- Verify that only valid email addresses are retained.
- Confirm that the `domain` field is correctly populated with the domain extracted from the email.

## Docker Setup

The project uses Docker to containerize the Python application and PostgreSQL database. The following files are used:

- **Dockerfile**: Defines the environment and dependencies for the Python application.
- **docker-compose.yml**: Configures the application and PostgreSQL containers.

### Dockerfile

The `Dockerfile` will set up the environment for the Python application. It includes installing dependencies, downloading the PostgreSQL JDBC driver, and configuring the container.

### docker-compose.yml

This configuration defines the services, including the Python app container (`app`) and PostgreSQL container (`db`). It now makes use of Docker secrets for securely storing the PostgreSQL password.

### Building and Running the Docker Containers

The Docker Compose file configures two services:
- **app**: The Python application container that runs the ETL process.
- **db**: The PostgreSQL database container.

Run the following command to build and start both containers:

```
docker-compose up --build
```

### Stopping the Docker Containers

To stop the running containers:

```
docker-compose down
```

## Deliverables

1. Python script(s) for the ETL process (`etl_script.py`).
2. SQL queries (`queries.sql`) and table creation script (`create_table.sql`).
3. Dockerfile and Docker Compose configuration (`docker-compose.yml`).
4. README documentation.
