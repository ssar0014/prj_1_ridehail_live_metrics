## Ridehail Live Metrics Project

In this project, we tackle the challenge of reporting live metrics of ridehail vehicles. There are 3 major components:
1. Data Generator - This is a fake data generator that will be producing messages to emulate ridehail service APIs responses. These will be json/noSql message format documents that contain information about the ride - vehicle, driver, customer, location, timestamps, status updates etc
2. Streaming Queue - This will serve as the connecting tissue between the data generator and the analytics service, allowing messages to flow through, we will be using the Kafka/Zookeeper stack for this
3. Analytics Service - This will be where the majority of the work is done. Once the messages come through from the source, the analytics service will then process it in real time and populate the data lakehouse. The end users will then be fed with a dashboard updating in real time where they will be able to track various metrics. 

This is a work in progress, and I will be updating it as I make more of it.


### Stack already in use:
1. Kafka - KRaft Mode - 2 controllers, 3 brokers
2. Python Data Generator
3. Apache Druid
4. Postgres - as the metadata store for Druid for streaming data
5. Postgres - as the data warehouse for transactional/historical data

### Stack yet to be installed (Final Stack TBD):
1. Apache Flink as the streaming analytics engine
2. DBT as the batch analytics engine
3. Dagster for orchestrating the pipelines
4. Apache Superset as the dashboard application

Update: Fake data generator now also includes `Mimesis` in addition to `Faker` for better control over schema-defined data


### Data Architecture

1. **Kafka (Streaming Ingestion Queue)**

* Kafka receives real-time ride events from the data generator.
* Messages are produced for:
    * `ride_events`: Ride status updates (e.g., `driver_assigned`, `ride_started`, `ride_completed`).
    * `user_events`: User actions (e.g., `new_driver_signup`, `customer_rating_submission`).
    * `vehicle_events`: Vehicle availability updates.

2. **Flink Overview** 

* Consume raw ride data from Kafka (`users`, `rides`, etc.).
* Process & Enrich Data using Flink:
* Add computed fields (e.g., trip duration, distance).
* Filter or clean missing/invalid data.
* Perform real-time aggregations (e.g., average ride cost per minute).
* Sink the processed data back to Kafka which can send it to Druid or Icerberg (into MinIO via Trino).

_Setting Up the Flink Job_

* We'll use Flink's Kafka Source and Druid Sink to send enriched data into Druid.

Install Required Dependencies

```
# Install required Flink connectors
FLINK_HOME=/path/to/flink  # Update with your Flink installation path

# Flink Kafka Connector
wget https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/1.15.2/flink-connector-kafka-1.15.2.jar -P $FLINK_HOME/lib

# Flink Druid Connector
wget https://repo1.maven.org/maven2/org/apache/druid/extensions/contrib/druid-flink/0.23.0/druid-flink-0.23.0.jar -P $FLINK_HOME/lib
```

_Writing the Flink Job_

* Create a Flink job (FlinkDruidPipeline.py for PyFlink).

```
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.datastream.connectors.druid import DruidSink
from pyflink.common.serialization import SimpleStringSchema
import json

def enrich_data(ride_json):
    ride = json.loads(ride_json)
    ride["trip_duration"] = ride["end_time"] - ride["start_time"]
    ride["cost_per_km"] = ride["fare_amount"] / ride["distance"]
    return json.dumps(ride)

env = StreamExecutionEnvironment.get_execution_environment()

# Kafka Source
kafka_source = KafkaSource.builder() \
    .set_bootstrap_servers("localhost:9092") \
    .set_topics("rides") \
    .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
    .set_value_only_deserializer(SimpleStringSchema()) \
    .build()

# Read from Kafka
ride_stream = env.from_source(kafka_source, watermark_strategy=None, source_name="Kafka Source")

# Enrich Data
enriched_stream = ride_stream.map(enrich_data)

# Druid Sink
druid_sink = DruidSink.builder() \
    .set_druid_coordinator_url("http://localhost:8081") \
    .set_data_source("ride_events") \
    .build()

# Write to Druid
enriched_stream.sink_to(druid_sink)

env.execute("Flink to Druid Pipeline")
```

📌 _Kafka → Flink → Druid Flow_

* Druid will consume data directly from Kafka topics.
    * Kafka Topic (rides) → Flink (enriches ride data) → Druid (aggregates & serves queries).
    * Flink can also store enriched data in Kafka (enriched_rides) for further processing.

* Once the pipeline is running, create a Druid ingestion spec (ride_events.json):

```
{
  "type": "kafka",
  "spec": {
    "dataSchema": {
      "dataSource": "ride_events",
      "parser": {
        "type": "string",
        "parseSpec": {
          "format": "json",
          "timestampSpec": {
            "column": "start_time",
            "format": "iso"
          },
          "dimensionsSpec": {
            "dimensions": ["ride_id", "driver_id", "customer_id"]
          }
        }
      }
    },
    "tuningConfig": {
      "type": "kafka"
    },
    "ioConfig": {
      "topic": "ride_events",
      "consumerProperties": {
        "bootstrap.servers": "localhost:9092"
      }
    }
  }
}
```

_Submit to Druid_

```
curl -X POST -H "Content-Type: application/json" -d @ride_events.json http://localhost:8081/druid/indexer
```

3. **Druid (Real-time OLAP for Recent Data)**

* Consumes Kafka topics (Streaming ingestion)
* Stores recent data (last few weeks) in a real-time optimized OLAP store.
* Supports fast, aggregated queries (e.g., “Total rides per city in the last 24 hours”).
* Queries come from Trino or Superset.

4. **Postgres (Historical Transactional Data)**

* Stores normalized, structured data for transactional queries.
* Holds historical rides in a batch-processed dimensional model.

5. **MinIO + Iceberg (Long-Term Storage)**

* Stores older data (>30 days) as Parquet-backed Iceberg tables.
* Query via Trino to offload old data from Postgres.

📌 _Querying Druid from Trino_

* Trino can federate queries between Postgres, Iceberg, and Druid:

```
SELECT driver_id, COUNT(*) AS total_rides
FROM druid.ride_events
WHERE ride_timestamp >= NOW() - INTERVAL '1 DAY'
GROUP BY driver_id;
```

📌 **Summary**
* Kafka -> Streaming data pipeline
* Flink -> Stream processing for sending enriched streaming data to Druid
* Druid	-> Fast OLAP queries on recent ride data
* Postgres -> Transactional DB for structured historical data
* MinIO + Iceberg -> Long-term batch storage for historical analytics
* Trino -> Query engine federating across all sources
* Superset -> Dashboards querying Druid & Trino