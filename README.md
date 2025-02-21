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

2. **Druid (Real-time OLAP for Recent Data)**

* Consumes Kafka topics (Streaming ingestion)
* Stores recent data (last few weeks) in a real-time optimized OLAP store.
* Supports fast, aggregated queries (e.g., “Total rides per city in the last 24 hours”).
* Queries come from Trino or Superset.

3. **Postgres (Historical Transactional Data)**

* Stores normalized, structured data for transactional queries.
* Holds historical rides in a batch-processed dimensional model.

4. **MinIO + Iceberg (Long-Term Storage)**

* Stores older data (>30 days) as Parquet-backed Iceberg tables.
* Query via Trino to offload old data from Postgres.

📌 _How Druid Ingests Data from Kafka_
* Druid will consume data directly from Kafka topics.

1️⃣ _Kafka → Druid Streaming Ingestion_
Druid’s native Kafka ingestion will automatically consume topics like ride_events and keep recent ride data in memory for ultra-fast queries.

```
{
  "type": "kafka",
  "spec": {
    "dataSchema": {
      "dataSource": "ride_events",
      "dimensionsSpec": {
        "dimensions": ["ride_id", "driver_id", "customer_id", "status", "pickup_location", "dropoff_location"]
      },
      "timestampSpec": {
        "column": "ride_timestamp",
        "format": "iso"
      }
    },
    "ioConfig": {
      "type": "kafka",
      "consumerProperties": {
        "bootstrap.servers": "localhost:9092"
      },
      "topic": "ride_events",
      "inputFormat": {
        "type": "json"
      }
    },
    "tuningConfig": {
      "type": "kafka"
    }
  }
}
```

📌 _Querying Druid from Trino_
Trino can federate queries between Postgres, Iceberg, and Druid:

```
SELECT driver_id, COUNT(*) AS total_rides
FROM druid.ride_events
WHERE ride_timestamp >= NOW() - INTERVAL '1 DAY'
GROUP BY driver_id;
```

📌 **Summary**
* Kafka -> Streaming data pipeline
* Druid	-> Fast OLAP queries on recent ride data
* Postgres -> Transactional DB for structured historical data
* MinIO + Iceberg -> Long-term batch storage for historical analytics
* Trino -> Query engine federating across all sources
* Superset -> Dashboards querying Druid & Trino