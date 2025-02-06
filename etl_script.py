import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_extract, to_date, from_unixtime
from pyspark.sql.utils import AnalysisException


try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: The 'load_dotenv' library is required but not installed.")
    print("You can install it by running: pip install load_dotenv")
    exit(1)  # Exit the script to prevent further errors


def get_postgres_password(secret_path: str) -> str:
    """Securely read PostgreSQL password from Docker Secret."""
    try:
        with open(secret_path, "r") as f:
            password = f.read().strip()
    except FileNotFoundError:
        print("Error: PostgreSQL password secret not found.")
        exit(1)
    return password


def setup_logging() -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        format='%(asctime)s - %(message)s',
        level=logging.INFO
    )
    return logging.getLogger(__name__)


def extract_data(spark: SparkSession, input_file: str) -> 'DataFrame':
    """Extract data from a CSV file and load it into a Spark DataFrame."""
    try:
        df = spark.read.csv(input_file, header=True, inferSchema=False)
        logging.info(f"Successfully loaded {input_file} into a DataFrame.")
        
    except Exception as e:
        logging.error(f"Error loading data from {input_file}: {e}")
        raise

    return df


def transform_data(df: 'DataFrame') -> 'DataFrame':
    """Transform the data: format signup_date, filter invalid emails, and extract domain."""
    try:
        df = df.filter(col("email").rlike(r"^[^@]+@[^@]+\.[^@]+$")) \
            .withColumn("signup_date", to_date(from_unixtime(col("signup_date")))) \
            .withColumn("domain", regexp_extract(col("email"), r'@([A-Za-z0-9.-]+)', 1)) \
            .withColumn("user_id", col("user_id").cast("int"))
    except AnalysisException as e:
        logging.error(f"Error during data transformation: {e}")
        raise
    return df


def load_data_to_postgresql(df: 'DataFrame', jdbc_url: str, table_name: str,
                            username: str, password: str) -> None:
    """Load the transformed data into a PostgreSQL database."""
    try:
        df.write.format("jdbc").options(
            url=jdbc_url,
            driver="org.postgresql.Driver",
            dbtable=table_name,
            user=username,
            password=password
        ).mode('append').save()  # 'overwrite' or 'append'
        logging.info(f"Successfully loaded data into {table_name}.")
    except Exception as e:
        logging.error(f"Error loading data to PostgreSQL: {e}")
        raise


def etl_pipeline(input_file: str, jdbc_url: str, table_name: str, username: str,
                 password: str) -> None:
    """Run the ETL pipeline: extract, transform, and load the data."""
    spark = SparkSession.builder \
        .appName("ETL Pipeline") \
        .config("spark.jars", "/opt/spark/jars/postgresql-42.2.24.jar") \
        .getOrCreate()

    # Extract: Load data from CSV
    df = extract_data(spark, input_file)

    # Transform
    df = transform_data(df)

    # Load
    load_data_to_postgresql(df, jdbc_url, table_name, username, password)

    print("ETL process completed successfully.")
    spark.stop()


if __name__ == "__main__":
    logger = setup_logging()

    load_dotenv()

    # Get environment variables
    JDBC_URL: str = os.getenv("JDBC_URL")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_TABLE: str = os.getenv("POSTGRES_TABLE")
    SECRET_PATH: str = os.getenv("SECRET_POSTGRES_PASSWORD_PATH")
    POSTGRES_PASSWORD: str = get_postgres_password(SECRET_PATH)

    print(f"Connecting to DB {POSTGRES_TABLE} as {POSTGRES_USER}")  # Debugging (hides password)

    input_file: str = "data.csv"

    try:
        etl_pipeline(input_file, JDBC_URL, POSTGRES_TABLE, POSTGRES_USER, POSTGRES_PASSWORD)
    except Exception as e:
        logger.error(f"ETL process failed: {e}")
