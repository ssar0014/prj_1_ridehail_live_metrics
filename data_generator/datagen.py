import time
import json
import ast
from typing import Dict, Any, Optional, List
from faker import Faker
from faker_vehicle import VehicleProvider
import random
from datetime import datetime, timedelta


class RideDataGenerator:
    def __init__(self):
        """
        Initialize the ride data generator.

        :param delay: The delay (in seconds) between generating records for a trip.
        """
        self.faker = Faker()
        self.faker.add_provider(VehicleProvider)

    def vehicle_model_schema(self) -> Dict[str, str]:
        vehicle_model_schema = {
            "vehicle_id": self.faker.uuid4(),
            "vehicle_identification_number": self.faker.vin(),
            "vehicle_license_plate": self.faker.license_plate(),
            "vehicle_make": self.faker.vehicle_make(),
            "vehicle_model": self.faker.vehicle_model(),
            "vehicle_category": self.faker.vehicle_category(),
            "vehicle_model_year": f"MY{self.faker.vehicle_year()}",
        }

        return vehicle_model_schema

    def user_model_schema(self, user_type: str, gender: str) -> Dict[str, str]:
        user_model_schema = {
            "user_id": self.faker.uuid4(),
            "first_name": (
                self.faker.first_name_male()
                if gender == "M"
                else self.faker.first_name_female()
            ),
            "last_name": self.faker.last_name(),
            "user_name": self.faker.user_name(),
            "phone_number": self.faker.basic_phone_number(),
            # used a beta distribution to skew values more towards the higher end
            # usually user ratings are high
            "user_rating": round(3.5 + (random.betavariate(4, 1) * 1.5), 1),
            "created_at": self.faker.date_time_this_year().isoformat(),
            "is_active": random.choice([True, False]),
            "user_type": user_type,
            "user_schema_version": "v1.0",  # For schema versioning
        }

        if user_type == "driver":
            # Add driver-specific fields
            user_model_schema.update(
                {
                    "email": f"{user_model_schema['first_name']}.{user_model_schema['last_name']}@{self.faker.domain_name()}",
                    "driver_license_number": self.faker.license_plate(),  # Mocking license plate as a license number
                    "driver_rating_count": random.randint(10, 500),
                    "years_of_experience": random.randint(1, 20),
                    "vehicle_id": self.vehicle_model_schema()[
                        "vehicle_id"
                    ],  # Reference vehicle_id
                }
            )
        elif user_type == "customer":
            # Add customer-specific fields
            user_model_schema.update(
                {
                    "email": f"{user_model_schema['first_name']}.{user_model_schema['last_name']}@{self.faker.domain_name()}",
                    "customer_loyalty_status": random.choice(
                        ["Bronze", "Silver", "Gold", "Platinum"]
                    ),
                    "total_rides": random.randint(1, 200),
                    "average_fare_amount": round(random.uniform(5.0, 100.0), 2),
                }
            )
        return user_model_schema

    def start_trip(self) -> Dict[str, Any]:
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

        return {
            "trip_id": self.faker.uuid4(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "start_location": start_location,
            "end_location": end_location,
            "status": "started",
        }


# Example Usage
if __name__ == "__main__":
    # Create an instance of the RideDataGenerator
    trip_generator = RideDataGenerator()
    print(
        trip_generator.start_trip(),
    )
