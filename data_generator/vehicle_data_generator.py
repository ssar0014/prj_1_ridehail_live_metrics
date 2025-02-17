from typing import Dict
from faker import Faker
from faker_vehicle import VehicleProvider
import mimesis
import mimesis.random


class VehicleDataGenerator:
    def __init__(self):
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


# Example Usage
if __name__ == "__main__":
    vehicle = VehicleDataGenerator()
    print(
        vehicle.vehicle_model_schema(),
    )
