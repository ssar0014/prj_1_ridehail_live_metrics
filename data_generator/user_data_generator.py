import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any
from faker import Faker
import mimesis
from vehicle_data_generator import VehicleDataGenerator


class UserDataGenerator:
    def __init__(self):
        self.faker = Faker()
        self.field = mimesis.Field(mimesis.Locale.EN)
        self.user_id_counter = 0  # Ensures unique incrementing `_id`

    def generate_customer_credit_card_details(self) -> Dict[str, str]:
        """Generates fake credit card details for customers."""
        card_type = random.choice(
            [
                mimesis.enums.CardType.AMERICAN_EXPRESS,
                mimesis.enums.CardType.VISA,
                mimesis.enums.CardType.MASTER_CARD,
            ]
        )
        payment = mimesis.Payment()
        return {
            "card_type": card_type.value,
            "card_number": payment.credit_card_number(card_type),
            "expiry_date": payment.credit_card_expiration_date(minimum=11, maximum=25),
            "card_cvv": payment.cvv(),
        }

    def create_base_user_model_schema(
        self, user_type: str, gender: str
    ) -> Dict[str, Any]:
        """Generates a base user model schema with essential fields."""
        self.user_id_counter += 1  # Ensures unique incrementing `_id`

        return {
            "_id": self.user_id_counter,  # Properly increments
            "user_id": self.field("uuid"),
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
                min_year=1940, max_year=(datetime.now() - timedelta(days=6570)).year
            )
            .isoformat(),
            "gender": gender,
            "address": mimesis.Address().address(),
            "user_rating": round(
                3.5 + (random.betavariate(4, 1) * 1.5), 1
            ),  # Skewed right
            "created_at": self.faker.date_time_this_year().isoformat(),
            "is_active": random.choice([True, False]),
            "user_type": user_type,  # Use the provided user_type
            "user_schema_version": self.field("version"),
        }

    def extend_user_model_schema(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extends the base schema with additional fields based on user type."""
        email = f"{user_data['first_name'].lower()}.{user_data['last_name'].lower()}_{self.field('person.email', domains=['gmail.com', 'yahoomail.com', 'hotmail.com'])}"

        if user_data["user_type"] == "driver":
            user_data.update(
                {
                    "email": email,
                    "driver_license_number": self.faker.license_plate(),
                    "driver_rating_count": random.randint(10, 500),
                    "years_of_experience": random.randint(1, 20),
                    "driver_vehicle_schema": VehicleDataGenerator().vehicle_model_schema(),
                    "payment_details": {
                        "account_number": self.faker.bban(),
                        "bank_country": self.faker.bank_country(),
                        "international_bank_account_number": self.faker.iban(),
                        "account_swift_number": self.faker.swift11(),
                    },
                }
            )
        elif user_data["user_type"] == "customer":
            user_data.update(
                {
                    "email": email,
                    "customer_loyalty_status": random.choice(
                        ["Bronze", "Silver", "Gold", "Platinum", "Diamond"]
                    ),
                    "total_rides": random.randint(1, 200),
                    "average_fare_amount": round(random.uniform(5.0, 100.0), 2),
                    "credit_card": self.generate_customer_credit_card_details(),
                }
            )

        return user_data  # Return the updated dictionary


# Example Usage
if __name__ == "__main__":
    user_generator = UserDataGenerator()

    for _ in range(5):
        base_user = user_generator.create_base_user_model_schema(
            user_type="driver", gender="M"
        )
        full_user = user_generator.extend_user_model_schema(base_user)
        print(json.dumps(full_user, indent=4))
