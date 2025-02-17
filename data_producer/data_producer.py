from data_generator.user_data_generator import UserDataGenerator
from kafka import KafkaProducer
import json
import time
import random

user_data_generator = UserDataGenerator()


def get_user_data(user_type, gender):
    base_user = user_data_generator.create_base_user_model_schema(
        user_type=user_type, gender=gender
    )
    full_user = user_data_generator.extend_user_model_schema(base_user)
    return full_user


def stream_data():
    random_user_type = random.choice(["driver", "customer"])
    random_gender_type = random.choice(["M", "F"])

    result = get_user_data(user_type=random_user_type, gender=random_gender_type)

    producer_obj = KafkaProducer(
        bootstrap_servers=["localhost:9092"], max_block_ms=5000
    )
    producer_obj.send("ride_created", json.dumps(result).encode("utf-8"))
    return True


if __name__ == "__main__":
    print(stream_data())
