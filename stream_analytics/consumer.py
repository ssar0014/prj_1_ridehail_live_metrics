from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
import os

# Set up the execution environment
env = StreamExecutionEnvironment.get_execution_environment()
settings = EnvironmentSettings.in_streaming_mode()

# Create table environment
t_env = StreamTableEnvironment.create(
    stream_execution_environment=env, environment_settings=settings
)

# Add Kafka connector dependency
kafka_sql_jar = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "jars/flink-sql-connector-kafka-3.4.0-1.20.jar",
)
kafka_jar = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "jars/flink-connector-kafka-3.4.0-1.20.jar",
)

t_env.get_config().get_configuration().set_string(
    "pipeline.jars", f"file://{kafka_sql_jar};file://{kafka_jar}"
)
t_env.get_config().set("parallelism.default", "1")

# Define source table DDL
src_ddl = """
    CREATE TABLE users_schema_kafka (
        _id INT,
        user_id VARCHAR,
        first_name VARCHAR,
        last_name VARCHAR,
        user_name VARCHAR,
        phone_number VARCHAR,
        date_of_birth VARCHAR,
        gender VARCHAR,
        address VARCHAR,
        user_rating DOUBLE,
        created_at TIMESTAMP(3),
        is_active BOOLEAN,
        user_type VARCHAR,
        user_schema_version VARCHAR,
        email VARCHAR,
        customer_loyalty_status VARCHAR,
        total_rides INT,
        average_fare_amount DOUBLE,
        WATERMARK FOR created_at AS created_at - INTERVAL '30' SECONDS
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'users_schema',
        'properties.bootstrap.servers' = 'localhost:29092,localhost:39092,localhost:49092',
        'properties.group.id' = 'users_schema',
        'format' = 'json',
        'value.format' = 'json',
        'properties.auto.offset.reset' = 'earliest',
        'json.timestamp-format.standard' = 'ISO-8601'
    );
"""

# Execute the source DDL
t_env.execute_sql(src_ddl)

# Create and initiate loading of source table
source_table = t_env.from_path("users_schema_kafka")

# Print source schema for debugging
print("\nSource Schema")
source_table.print_schema()

# Define sink table DDL
sink_ddl = """
    CREATE TABLE aggregate_user_ratings (
        gender VARCHAR,
        window_interval TIMESTAMP(3),
        total_rides INT,
        avg_user_rating DOUBLE
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'aggregate_user_ratings',
        'properties.bootstrap.servers' = 'localhost:29092,localhost:39092,localhost:49092',
        'format' = 'json',
        'value.format' = 'json',
        'properties.processing-mode' = 'exactly_once',
        'properties.enable.idempotence' = 'true'
    )
"""

# Execute the sink DDL
t_env.execute_sql(sink_ddl)
sink_table = t_env.from_path("aggregate_user_ratings")

# Print sink schema for debugging
print("\nSink Schema")
sink_table.print_schema()

# Define SQL query for aggregation
sql = """
    INSERT INTO aggregate_user_ratings
    SELECT
        gender,
        TUMBLE_END(created_at, INTERVAL '30' SECONDS) AS window_interval,
        SUM(total_rides) AS total_rides,
        AVG(user_rating) AS avg_user_rating
    FROM users_schema_kafka
    GROUP BY
        TUMBLE(created_at, INTERVAL '30' SECONDS),
        gender;
"""

# Execute the query
res_table = t_env.execute_sql(sql)
source_table.execute().print()
# Check job status (optional)
try:
    job_status = res_table.get_job_client().get_job_status()
    print(f"Job Status: {job_status}")
except Exception as e:
    print(f"Error getting job status: {e}")
