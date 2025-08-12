from typing import TYPE_CHECKING

import seleniumwire.webdriver
from requests.exceptions import JSONDecodeError

from db.transfer import LeadGenResultStatus, LeadGenResult
from db.gologin import GologinApikeysRepository
from parser.sessions import LeadsGenerationSession
from parser.parser import exceptions as parser_exceptions
from parser.utils.sms import exceptions as sms_exceptions
from parser import exceptions

if TYPE_CHECKING:
    from parser.main import PlatformLeadsService
else:
    PlatformLeadsService = object


def _retrieve_driver(
        self: PlatformLeadsService,
        lead_id: int,
        session_id: int) -> tuple[int, seleniumwire.webdriver.Chrome]:
    for _ in range(10):
        proxy = self._proxy_service.next()

        try:
            return self._drivers_service.get_desctop(
                proxy=proxy,
                worker_id=[session_id, lead_id]
            )
        except JSONDecodeError as e:
            print(f"LEAD #{lead_id} GOLOGIN RESPONSE FAILED - {e} | {repr(e)}")

            try:
                GologinApikeysRepository().annihilate_current()
            except Exception as e:
                self._db_service.change_status(
                    session_id=session_id,
                    lead_id=lead_id,
                    status=LeadGenResultStatus.FAILED,
                    error=f"GOLOGIN RESPONSE FAILED: \n\n{repr(e)}\n\n{e}"
                )

                raise e

            print(f"ANNIHILATED UNRELEVANT GOLOGIN APIKEY")
        except Exception as e:
            print(f"LEAD #{lead_id} FAILED - {e} {repr(e)}")

            if "proxyerror" in str(e).lower():
                continue
            elif ("expecting value" in str(e).lower()) or (
                    "navigator" in str(e).lower()):
                try:
                    GologinApikeysRepository().annihilate_current()
                except Exception as e:
                    self._db_service.change_status(
                        session_id=session_id,
                        lead_id=lead_id,
                        status=LeadGenResultStatus.FAILED,
                        error=f"GOLOGIN RESPONSE FAILED: \n\n{repr(e)}\n\n{e}"
                    )

                    raise e

                print(f"ANNIHILATED UNRELEVANT GOLOGIN APIKEY")

            else:
                print(f"ERROR STR LOWER : {str(e).lower()}")

                raise e
    else:
        print(f"LEAD #{lead_id} CANT RUN GOLOGIN")
        self._db_service.change_status(
            session_id=session_id,
            lead_id=lead_id,
            status=LeadGenResultStatus.FAILED,
            error=f"CANT RUN GOLOGIN AFTER 15 RETRY"
        )
        raise Exception(f"LEAD #{lead_id} CANT RUN GOLOGIN")


def session_results_commiter():
    def wrapper(
            *args,
            lead_id: int = None,
            __recursion_count: int = 0,
            **kwargs):
        self: PlatformLeadsService = args[0]

        session_id, session = (
            kwargs.get("session_id"), kwargs.get("session")
        )

        if __recursion_count > 20:
            self._leads_db.change_status(
                lead_id=lead_id,
                session_id=session_id,
                status=LeadGenResultStatus.FAILED,
                error=f"CANNOT MAKE LEAD [20 RETRIES]"
            )

        session: LeadsGenerationSession

        if lead_id is None:
            _, lead_id = self._db_service.add(
                session_id=session_id,
                result=LeadGenResult(
                    session_id=session_id,
                    status=LeadGenResultStatus.PROGRESS,
                    ref_link=convert_ref_link(session.ref_link),
                    error="",
                )
            )

        pid, driver = _retrieve_driver(self=self,
                                       lead_id=lead_id,
                                       session_id=session_id)

        print(f"=== LEAD #{lead_id} STARTED ===")

        parser = self._parser(
            driver=driver,
            session_id=session_id,
            lead_id=lead_id
        )

        print(f"LEAD #{lead_id} BROWSER INITED")

        kwargs |= {"lead_id": lead_id,
                   "parser": parser,
                   "session": LeadsGenerationSession(ref_link=session.ref_link)}

        try:
            func(*args, **kwargs)
        except parser_exceptions.TraficBannedError as e:
            print(f"LEAD #{lead_id} TRAFIC BANNED ERROR [{str(e)}] [{repr(e)}]")

            return wrapper(*args, lead_id=lead_id, __recursion_count=__recursion_count+1, **kwargs)
        except sms_exceptions.NumberGettingException as e:
            print(f"LEAD #{lead_id} CANNOT GET PHONE NUMBER AFTER ALL ATTEMPTS, ERROR WITH SMS SERVICE! [{str(e)}] [{repr(e)}]")

            self._leads_db.change_status(
                lead_id=lead_id,
                session_id=session_id,
                status=LeadGenResultStatus.FAILED,
                error=f"CANNOT GET PHONE NUMBER AFTER ALL ATTEMPTS, ERROR WITH SMS SERVICE! [{str(e)}] [{repr(e)}]"
            )
            raise e
        except parser_exceptions.UnsolvableCaptchaError as e:
            print(f"LEAD #{lead_id} UNSOLVABLE CAPTCHA! [{str(e)}] [{repr(e)}]")

            return wrapper(*args, lead_id=lead_id, __recursion_count=__recursion_count+1, **kwargs)
        except (exceptions.ProfileBannedError, parser_exceptions.NumberBlockedByStolotoError, parser_exceptions.RegOtpEnteringError, parser_exceptions.AccountRegistrationPageError) as e:
            print(f"LEAD #{lead_id} MAYBE BANNED BY STOLOTO [{str(e)}] [{repr(e)}]")

            return wrapper(*args, lead_id=lead_id, __recursion_count=__recursion_count+1, **kwargs)
        except exceptions.ReloadLead as e:
            print(str(e))

            return wrapper(*args, lead_id=lead_id, __recursion_count=__recursion_count+1, **kwargs)
        except exceptions.ErrorAfterRegistration:
            return
        except Exception as e:
            print(f"LEAD #{lead_id} UNKNOWN ERROR, RELOAD LEAD - [{str(e)}] [{repr(e)}]")

            return wrapper(*args, lead_id=lead_id, __recursion_count=__recursion_count+1, **kwargs)

    return wrapper
