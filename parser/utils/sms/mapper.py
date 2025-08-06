from .elsms import ElSmsSMSCodesService
from .helpersms import HelperSMSService

from db.sms import (ElSmsServiceApikeyRepository,
                    HelperSmsServiceApikeyRepository)


class ELSMS:
    KEY = "E"


class HELPERSMS:
    KEY = "S"


SMS_SERVICES_MAPPER = {
    ELSMS.KEY: ElSmsSMSCodesService,
    HELPERSMS.KEY: HelperSMSService
}

SMS_DB_REPOSITORY_MAPPER = {
    ELSMS.KEY: ElSmsServiceApikeyRepository(),
    HELPERSMS.KEY: HelperSmsServiceApikeyRepository(),
}
