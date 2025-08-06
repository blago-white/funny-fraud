from .base import BaseMailCredentialsFormatter


class HStockFormatter(BaseMailCredentialsFormatter):
    def __init__(self, credentials: str):
        self._raw_credentials = credentials.split("\n\n")

    @property
    def formated(self):
        jsoned_credentials = []

        for credential in self._raw_credentials:
            credential = credential.split("\n")

            print("CRED", credential)

            jsoned_credentials.append({
                "mail": credential[0].split(": ")[-1],
                "password": credential[1].split(": ")[-1],
                "number": credential[2].split(": ")[-1],
            })

        return jsoned_credentials
