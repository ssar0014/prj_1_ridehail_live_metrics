## Ridehail Live Metrics Project

In this project, we tackle the challenge of reporting live metrics of ridehail vehicles. There are 3 major components:
1. Data Generator - This is a fake data generator that will be producing messages to emulate ridehail service APIs responses. These will be json/noSql message format documents that contain information about the ride - vehicle, driver, customer, location, timestamps, status updates etc
2. Streaming Queue - This will serve as the connecting tissue between the data generator and the analytics service, allowing messages to flow through, we will be using the Kafka/Zookeeper stack for this
3. Analytics Service - This will be where the majority of the work is done. Once the messages come through from the source, the analytics service will then process it in real time and populate the data lakehouse. The end users will then be fed with a dashboard updating in real time where they will be able to track various metrics. 

The architecture for this is as follows:
Data Generator (API/Python) -> Kafka -> Flink -> Iceberg Lakehouse -> Dbt -> Streamlit

The whole pipeline will be orchestrated via Airflow or Dagster.

This is a work in progress, and I will be updating it as I make more of it.
