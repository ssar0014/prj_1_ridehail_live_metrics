from data_generator.user_data_generator import UserDataGenerator
from kafka import KafkaProducer
import json
import time
import random

# Initialize Kafka Producer (outside the loop)
producer = KafkaProducer(
    bootstrap_servers=["localhost:29092", "localhost:39092"],
    key_serializer=str.encode,  # Ensures key is in bytes
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),  # JSON encoding
)

# Initialize User Data Generator
user_data_generator = UserDataGenerator()


def get_user_data(user_type, gender):
    base_user = user_data_generator.create_base_user_model_schema(
        user_type=user_type, gender=gender
    )
    full_user = user_data_generator.extend_user_model_schema(base_user)
    return full_user


def stream_data(topic, user_type, n_msg):
    for x in range(n_msg):
        random_gender_type = random.choice(["M", "F"])
        user_data = get_user_data(user_type=user_type, gender=random_gender_type)
        if user_type == "driver":
            producer.send(topic=topic, key=user_type, value=user_data)
        else:
            producer.send(topic=topic, key=user_type, value=user_data)
        print(f"Message {x+1}/{n_msg} - {user_type} sent to Kafka.")
        time.sleep(random.uniform(0.1, 0.5))
    producer.flush()
    print(f"✅ Sent {n_msg} messages to Kafka for user_type={user_type}")
    return True


if __name__ == "__main__":
    table_name = "users_schema"
    for user_type in ["customer"]:
        stream_data(topic=table_name, user_type=user_type, n_msg=12000)
