## Ridehail Live Metrics Project

In this project, we tackle the challenge of reporting live metrics of ridehail vehicles. There are 3 major components:
1. Data Generator - This is a fake data generator that will be producing messages to emulate ridehail service APIs responses. These will be json/noSql message format documents that contain information about the ride - vehicle, driver, customer, location, timestamps, status updates etc
2. Streaming Queue - This will serve as the connecting tissue between the data generator and the analytics service, allowing messages to flow through, we will be using the Kafka/Zookeeper stack for this
3. Analytics Service - This will be where the majority of the work is done. Once the messages come through from the source, the analytics service will then process it in real time and populate the data lakehouse. The end users will then be fed with a dashboard updating in real time where they will be able to track various metrics. 

This is a work in progress, and I will be updating it as I make more of it.


### Stack already in use:
1. Kafka/Zookeeper
2. Python Data Generator

### Stack yet to be installed (Final Stack TBD):
1. Postgres as the batch ingestion warehouse
2. Apache Druid as the streaming ingestion warehouse
3. Apache Iceberg as Open Table format
4. MinIO as object storage
5. DBT as the batch analytics engine
6. Apache Flink as the streaming analytics engine
7. Dagster for orchestrating the pipelines
8. Apache Superset as the real time dashboard application

Update: Fake data generator now also includes `Mimesis` for better control over schema-defined data
