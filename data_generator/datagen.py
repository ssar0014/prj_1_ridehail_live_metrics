import time
import json
import ast
from typing import Dict, Any, Optional, List
from faker import Faker
import random
from datetime import datetime, timedelta


class RideDataGenerator:
    def __init__(self, delay: float = 5.0):
        """
        Initialize the ride data generator.

        :param delay: The delay (in seconds) between generating records for a trip.
        """
        self.faker = Faker()
        self.delay = delay

    def generate_trip(self) -> Dict[str, Any]:
        """
        Generate a single trip with initial details.

        :return: A dictionary representing a trip.
        """
        # Generate trip start and end times
        start_time = datetime.now()
        end_time = start_time + timedelta(
            minutes=random.randint(10, 60)
        )  # Trip duration between 10 and 60 minutes

        # Generate start and end geo-locations
        start_location = (self.faker.latitude(), self.faker.longitude())
        end_location = (self.faker.latitude(), self.faker.longitude())

        # Generate driver, customer, and car details
        driver = {
            "driver_id": self.faker.uuid4(),
            "name": self.faker.name(),
            "rating": round(random.uniform(4.0, 5.0), 1),
        }
        customer = {
            "customer_id": self.faker.uuid4(),
            "name": self.faker.name(),
            "phone_number": self.faker.phone_number(),
        }
        car = {
            "car_id": self.faker.uuid4(),
            "license_plate": self.faker.license_plate(),
            "make": self.faker.company(),
            "model": random.choice(["Sedan", "SUV", "Hatchback", "Luxury"]),
        }

        return {
            "trip_id": self.faker.uuid4(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "start_location": start_location,
            "end_location": end_location,
            "driver": driver,
            "customer": customer,
            "car": car,
            "status": "started",
        }


# Example Usage
if __name__ == "__main__":
    # Create an instance of the RideDataGenerator
    trip_generator = RideDataGenerator(delay=5.0)  # 5-second delay between records
    trip_1 = trip_generator.generate_trip()
    print(trip_1)
