import time
import json
import ast
from typing import Dict, Any, Optional, List
from faker import Faker
from faker_vehicle import VehicleProvider
import mimesis
import random
from datetime import datetime, timedelta

import mimesis.random


class RideDataGenerator:
    def __init__(self):
        """
        Initialize the ride data generator.

        :param delay: The delay (in seconds) between generating records for a trip.
        """
        self.faker = Faker()
        self.faker.add_provider(VehicleProvider)
        self.field = mimesis.Field(mimesis.Locale.EN)
        self.fieldset = mimesis.Fieldset(mimesis.Locale.EN)

    def vehicle_model_schema(self) -> Dict[str, str]:
        vehicle_model_schema = {
            "vehicle_id": self.field("uuid"),
            "vehicle_identification_number": self.faker.vin(),
            "vehicle_license_plate": self.faker.license_plate(),
            "vehicle_make": self.faker.vehicle_make(),
            "vehicle_model": self.faker.vehicle_model(),
            "vehicle_category": self.faker.vehicle_category(),
            "vehicle_model_year": f"MY{self.faker.vehicle_year()}",
        }

        return vehicle_model_schema

    def generate_customer_credit_card_details(self) -> Dict[str, str]:
        card_type = mimesis.random.Random().choice_enum_item(
            [
                mimesis.enums.CardType.AMERICAN_EXPRESS,
                mimesis.enums.CardType.VISA,
                mimesis.enums.CardType.MASTER_CARD,
            ]
        )
        card_number = mimesis.Payment().credit_card_number(card_type)
        card_expiry_date = mimesis.Payment().credit_card_expiration_date(
            minimum=11, maximum=25
        )
        card_cvv = mimesis.Payment().cvv()
        return {
            "card_type": card_type.value,
            "card_number": card_number,
            "expiry_date": card_expiry_date,
            "card_cvv": card_cvv,
        }

    def user_model_schema(self, user_type: str, gender: str) -> Dict[str, str]:
        user_model_schema = {
            "user_id": self.faker.uuid4(),
            "first_name": (
                self.field("first_name", gender=mimesis.enums.Gender.MALE)
                if gender == "M"
                else self.field("first_name", gender=mimesis.enums.Gender.FEMALE)
            ),
            "last_name": self.field("last_name"),
            "user_name": self.field("person.username", mask="U_d", drange=(100, 1000)),
            "phone_number": mimesis.Person().phone_number(),
            "date_of_birth": mimesis.Person()
            .birthdate(
                min_year=1940,
                max_year=(datetime.now() - timedelta(days=6570)).year,
            )
            .isoformat(),
            # used a beta distribution to skew values more towards the higher end
            # usually user ratings are high
            "user_rating": round(3.5 + (random.betavariate(4, 1) * 1.5), 1),
            "created_at": self.faker.date_time_this_year().isoformat(),
            "is_active": random.choice([True, False]),
            "user_type": user_type,
            "user_schema_version": self.field("version"),  # For schema versioning
        }

        if user_type == "driver":
            # Add driver-specific fields
            user_model_schema.update(
                {
                    "email": f"{user_model_schema['first_name'].lower()}.{user_model_schema['last_name'].lower()}_{self.field('person.email', domains=['gmail.com', 'yahoomail.com', 'hotmail.com'])}",
                    "driver_license_number": self.faker.license_plate(),  # Mocking license plate as a license number
                    "driver_rating_count": random.randint(10, 500),
                    "years_of_experience": random.randint(1, 20),
                    "vehicle_id": self.vehicle_model_schema()[
                        "vehicle_id"
                    ],  # Reference vehicle_id
                    "payment_details": {
                        "account_number": self.faker.bban(),
                        "bank_country": self.faker.bank_country(),
                        "international_bank_account_number": self.faker.iban(),
                        "account_swift_number": self.faker.swift11(),
                    },
                }
            )
        elif user_type == "customer":
            # Add customer-specific fields
            user_model_schema.update(
                {
                    "email": f"{user_model_schema['first_name'].lower()}.{user_model_schema['last_name'].lower()}_{self.field('person.email', domains=['gmail.com', 'yahoomail.com', 'hotmail.com'])}",
                    "customer_loyalty_status": random.choice(
                        ["Bronze", "Silver", "Gold", "Platinum", "Diamond"]
                    ),
                    "total_rides": random.randint(1, 200),
                    "average_fare_amount": round(random.uniform(5.0, 100.0), 2),
                    "credit_card": self.generate_customer_credit_card_details(),
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
        trip_generator.user_model_schema(user_type="driver", gender="M"),
        trip_generator.user_model_schema(user_type="customer", gender="F"),
    )
