import random
import string
from dataclasses import dataclass


class OwnerCredentalsGenerator:
    def get_random_owner_data(self) -> list[str]:
        password = self._get_random_password()

        return [
            self._get_random_date(),
            password,
            password,
            self._get_random_email()
        ]

    def _get_random_email(self):
        return f"{self._get_random_password()}@gmail.com"

    @staticmethod
    def _get_random_date() -> str:
        return f"{str(random.randint(1, 28)).zfill(2)}{str(random.randint(1, 12)).zfill(2)}{random.randint(1989, 1999)}"

    @staticmethod
    def _get_random_password():
        return "".join(
            [random.choice(
                random.choice([
                    string.ascii_lowercase,
                    string.ascii_uppercase
                ])
            ) for _ in range(9)] + ["-"] + [random.choice(string.digits)]
        )
