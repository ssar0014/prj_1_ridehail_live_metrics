from datagen import RideDataGenerator
from kafka import KafkaProducer
import json
import time


def get_data():
    return f"{RideDataGenerator().generate_trip()}"


def stream_data():
    result = get_data()
    producer_obj = KafkaProducer(
        bootstrap_servers=["localhost:9092"], max_block_ms=5000
    )
    producer_obj.send("ride_created", json.dumps(result).encode("utf-8"))
    return True


if __name__ == "__main__":
    stream_data()
