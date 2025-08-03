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


@dataclass
class AccountCredentials:
    mail_credentials: AccountMailCredentials
    number: int


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
        self.credentials = AccountCredentials(
            mail_credentials=AccountMailCredentials(
                addr=self.credentials[0][0],
                password=self.credentials[0][1],
                number=self.credentials[0][2]
            ),
            number=self.credentials[1]
        )

        self.status = STATUS_MAPPING.get(self.status, "f")
