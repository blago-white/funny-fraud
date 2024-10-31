import random
import time
import string

from selenium.webdriver.chrome.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from selenium_recaptcha_solver import RecaptchaSolver

from .sms.authenticator import SMSAuthenticator
from . import exceptions


def random_password():
    symbols = list(
        string.ascii_lowercase + string.ascii_uppercase + string.digits
    )

    random.shuffle(symbols)

    password = "".join([i for i in symbols[:10]])

    return password


def random_mail():
    mail = random_password() + "@gmail.com"

    return mail


class PlatformLoginParser:
    _driver: ChromiumDriver
    _solver: RecaptchaSolver

    _activation_id: int = 0
    _number: int = 0

    def __init__(self, driver: ChromiumDriver,
                 solver: RecaptchaSolver = None,
                 sms_service: SMSAuthenticator = None):
        self._driver = driver
        self._solver = solver or RecaptchaSolver(driver=driver)
        self._sms_service: SMSAuthenticator = sms_service or SMSAuthenticator()

    async def login(self, ref_link: str) -> tuple[int, int, str]:
        self._open_login_form(ref_link=ref_link)

        yield "> ✅ Open login form"

        exceptions_list: list[BaseException] = []

        for i in range(6):
            try:
                self._driver.execute_script(
                    """                    
                    var css = '.flocktory-widget-overlay { display: none!important; }',
                        head = document.head || document.getElementsByTagName('head')[0],
                        style = document.createElement('style');
                    
                    head.appendChild(style);
                    
                    style.type = 'text/css';
                    if (style.styleSheet){
                      style.styleSheet.cssText = css;
                    } else {
                      style.appendChild(document.createTextNode(css));
                    }        
                    """
                )

                await self._authenticate_number()
                # print("SUCCESS END AUTH")

                yield "> ✅ Phone number authenticated"

                break
            except (
                    Exception,
                    exceptions.BadPhoneNumber,
                    exceptions.AccountExists
                    ) as e:
#                 print("EXEPT", e)

                self._driver.execute_script(
                    f"""
                    location.href = '{ref_link}';
                    """
                )
                exceptions_list.append(e)
        else:
            raise exceptions.LoginFailedAfterRetries(
                "Retries fails reasons:\n" +
                "\n".join([f"- Error: {e}" for e in exceptions_list])
            )

        for _ in range(5):
            try:
                acc_data = self._enter_account_data()
                break
            except:
                self._driver.execute_script(
                    """
                    location.href = location.href;
                    """
                )
                time.sleep(10)
        else:
            raise exceptions.ErrorEnteringAccountData(
                "Error complete account data form"
            )

        yield f"> ✅ Account registred - {acc_data}"

        yield self._activation_id, self._number, acc_data

    def _enter_account_data(self):
        WebDriverWait(self._driver, 30).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/main/div/div[2]/form/div[2]/div/input"),
            ),
        )

        mail_field = self._driver.find_element(
            By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/main/div/div[2]/form/div[2]/div/input"
        )

        mail_field.click()

        mail = random_mail()

        mail_field.send_keys(mail)

        password_field = self._driver.find_element(
            By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/main/div/div[2]/form/div[3]/div/input"
        )

        password_field.click()

        password = random_password()

        password_field.send_keys(password)

        self._driver.implicitly_wait(1)

        self._driver.find_element(
            By.CSS_SELECTOR,
            "#__next > div.RootLayout_layout__AN70W > div.Wrap_wrap__YsCW8.Wrap_wrap__mYUid.PageLayout_wrap__bHTtx > div > main > div > div.Container_container__2bu_W > form > button"
        ).click()

        return f"{mail}:{password}"

    def _open_login_form(self, ref_link: str):
        self._driver.get(ref_link)

#         print("LOGIN STARTED")

    async def _authenticate_number(self):
        WebDriverWait(self._driver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html/body/div[1]/div/div[2]/div/main/div[2]/div/form/div[1]/div/input"),
            )
        )

        self._activation_id, self._number = await (
            self._sms_service.get_number()
        )

#         print(f"NUMBER: {self._number}")

        try:
            self._enter_phone_number()
#             print("PHONE")
            self._solve_captcha()
#             print("CAPTHA PASSED")
        except Exception as e:
            print(f"ERROROR BLYAT: {e}")

#             print(f"ERROR CAPTCHA {e}")
            if not self._try_click_get_sms_btn(raise_exception=False):
                await self._sms_service.cancel(activation_id=self._activation_id)
                raise e
        else:
            self._try_click_get_sms_btn()
        finally:
            self._driver.switch_to.parent_frame()

#         print(f"START RECEIVE: {self._number}")

        try:
            code = await self._receive_code()
        except exceptions.ForceLogin:
#             print("FORCED!!!")
            return

        self._enter_code(code=code)

    def _solve_captcha(self):
        WebDriverWait(self._driver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, "#__next > div.RootLayout_layout__AN70W > div.Wrap_wrap__YsCW8.Wrap_wrap__mYUid.PageLayout_wrap__bHTtx > div > main > div > div > form > div.Captcha_wrap__Ofz4J > div > div > div > div > iframe")
            )
        )

        self._solver.click_recaptcha_v2(
            iframe=self._driver.find_element(
                By.CSS_SELECTOR, '#__next > div.RootLayout_layout__AN70W > div.Wrap_wrap__YsCW8.Wrap_wrap__mYUid.PageLayout_wrap__bHTtx > div > main > div > div > form > div.Captcha_wrap__Ofz4J > div > div > div > div > iframe'
            )
        )

    def _enter_phone_number(self):
        phone_field = self._driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div[2]/div/main/div[2]/div/form/div[1]/div/input"
        )

        phone_field.click()

        for i in str(self._number)[1:]:
            time.sleep(.01)
            phone_field.send_keys(i)

    def _enter_code(self, code: str):
        WebDriverWait(self._driver, 120).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div/div[2]/div/main/div/div["
                           "2]/div/div/input[1]")
            )
        )

        code_digits = [
            "/html/body/div[1]/div/div[2]/div/main/div/div[2]/div/div/input[1]",
            "/html/body/div[1]/div/div[2]/div/main/div/div[2]/div/div/input[2]",
            "/html/body/div[1]/div/div[2]/div/main/div/div[2]/div/div/input[3]",
            "/html/body/div[1]/div/div[2]/div/main/div/div[2]/div/div/input[4]"
        ]

        self._driver.find_element(
            By.XPATH, "/html/body/div[1]/div/div[2]/div/main/div/div[2]/div/div/input[1]"
        ).click()

        for i in range(len(code)):
            self._driver.find_element(
                By.XPATH, code_digits[i]
            ).send_keys(code[i])

    async def _receive_code(self) -> str:
        code = None
        START_RECEIVING = time.time()

        while not code:
            self._try_click_get_sms_btn()

            if (time.time() - START_RECEIVING) > 60*1.5:
                await self._sms_service.cancel(activation_id=self._activation_id)
                raise exceptions.BadPhoneNumber("Not receive sms code")

            code = await self._sms_service.get_status(
                activate_id=self._activation_id
            )

#             print(f"CODE: {code}")

            time.sleep(1)

            if self.can_login or self.account_exists:
                await self._sms_service.cancel(activation_id=self._activation_id)

                if self.can_login:
                    raise exceptions.ForceLogin
                elif self.account_exists:
                    raise exceptions.AccountExists

        return code

    @property
    def can_login(self):
        return "Последний шаг" in self._get_title()

    @property
    def account_exists(self):
        return "Введите пароль для входа" in self._get_title()

    @property
    def no_sms_started(self):
        return "Войти или зарегистрироваться" in self._get_title()

    def _get_title(self):
        try:
            WebDriverWait(self._driver, 30).until(
                expected_conditions.presence_of_element_located(
                    (By.TAG_NAME, "h1")
                )
            )
        except:
            return False

        return self._driver.find_element(
            By.TAG_NAME, "h1"
        ).text

    def _try_click_get_sms_btn(self, raise_exception: bool = True):
        c = 0
        error = Exception

        while c < 100:
            try:
                self._driver.find_element(
                    By.XPATH, '//*[@id="__next"]/div/div[2]/div/main/div/div/form/button'
                ).click()
                return True
            except Exception as e:
                error = e

            c += 1

        if raise_exception:
            raise error

        return False
