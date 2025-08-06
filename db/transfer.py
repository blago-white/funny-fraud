from dataclasses import dataclass


@dataclass
class LeadGenResultStatus:
    FAILED = "f"
    SUCCESS = "s"
    SUCCES_NO_VERIFIED_MAIL = "n"
    PHONE_CODE_PROGRESS = "p"
    ACCOUNT_REG_PROGRESS = "a"
    MAIL_VERIFICATION_PROGRESS = "m"
    TICKET_PURCHASING = "t"


STATUS_MAPPING = {
    "f": LeadGenResultStatus.FAILED,
    "s": LeadGenResultStatus.SUCCESS,
    "n": LeadGenResultStatus.SUCCES_NO_VERIFIED_MAIL,
    "p": LeadGenResultStatus.PHONE_CODE_PROGRESS,
    "a": LeadGenResultStatus.ACCOUNT_REG_PROGRESS,
    "m": LeadGenResultStatus.MAIL_VERIFICATION_PROGRESS,
    "t": LeadGenResultStatus.TICKET_PURCHASING
}


@dataclass
class AccountMailCredentials:
    addr: str
    password: str
    number: int

    def __str__(self):
        return f"{self.addr}-{self.password}-{self.number}"

    @classmethod
    def get_deserialised(cls, serialized: str):
        deserialized = serialized.split("-")

        return AccountMailCredentials(
            addr=deserialized[0],
            password=deserialized[1],
            number=int(deserialized[2])
        )

    def is_valid(self):
        if not (self.addr and self.password and self.number):
            raise MailCredentialsValidationError(
                "Mail account credentials validation failed!"
            )


@dataclass
class AccountCredentials:
    mail_credentials: AccountMailCredentials
    number: int

    def __str__(self):
        return f"ac{self.number}|{str(self.mail_credentials)}ac"

    @classmethod
    def get_deserialized(cls, serialized: str, separated: bool = False):
        deserialized = serialized.split("ac")[1]

        return AccountCredentials(
            number=int(deserialized.split("|")[0]),
            mail_credentials=AccountMailCredentials.get_deserialised(
                deserialized.split("|")[-1]
            ),
        )


@dataclass
class LeadGenResult:
    session_id: int
    lead_id: int | None = None

    status: str = None
    error: str | None = None
    proxy: str | None = None
    credentials: AccountCredentials | tuple[tuple[str, str, int], int] = None
    ref_link: str | None = None

    def __post_init__(self):
        print(self.credentials, type(self.credentials))

        if (type(self.credentials) is not AccountCredentials) and self.credentials:
            self.credentials = AccountCredentials(
                mail_credentials=AccountMailCredentials(
                    addr=self.credentials[0][0],
                    password=self.credentials[0][1],
                    number=self.credentials[0][2]
                ),
                number=self.credentials[1]
            )

        self.status = STATUS_MAPPING.get(self.status, "f")
