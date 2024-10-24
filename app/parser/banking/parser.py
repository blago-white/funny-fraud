import copy
import time

from selenium.webdriver import Chrome
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

from . import _steps
from . import exceptions


class BaseBankingParser:
    _time_cached_status: float = 0

    _otp: str = None
    _owner_phone: str = None
    _driver: Chrome = None
    _authenticated: bool = False

    _DEFAULT_PIN: str = "1488"
    _DEFAULT_PASS: str = "Qe23E4Trls"

    _AUTHENTICATED_URL: str = "https://www.tbank.ru/mybank/"

    def __init__(self, owner_phone: str = None, driver: Chrome = None):
        self._owner_phone = owner_phone or self._owner_phone
        self._driver = driver or self._driver

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(BaseBankingParser, cls).__new__(cls)

        return cls.instance

    def add_phone(self, owner_phone: str):
        self._owner_phone = owner_phone

    def add_driver(self, driver: Chrome):
        self._driver = driver

    @property
    def phone(self) -> str | None:
        return self._owner_phone

    @property
    async def authenticated(self):
        if ((time.time() - self._time_cached_status) < (20*60)
                and self._authenticated):
            return self._authenticated

        if not ("https://www.tbank.ru/mybank/" in self._driver.current_url):
            self._driver.get(self._AUTHENTICATED_URL)

        try:
            WebDriverWait(self._driver, 20).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div/div/div/div["
                               "3]/main/div[2]/div[1]/div[1]/div/ul/li["
                               "5]/div[1]/div/div[1]/div[2]/div[1]/div["
                               "1]/a/span")
                ),
            )
        except:
            self._authenticated = False
        else:
            self._authenticated = True
            self._time_cached_status = time.time()

        return self._authenticated

    @property
    def current_auth_step(self):
        try:
            title = self._driver.find_element(
                By.ID, "form-title"
            ).text
        except:
            return False

        return _steps.get_by_title(
            title=title
        )

    def reset(self):
        self._driver.delete_all_cookies()

    def send_login_request(self):
        self._open_login_form()

    def enter_otp_code(self, code: str):
        self._otp = code

        self._enter_otp_code(code=code)

        START_COMMIT_TIME = time.time()

        while time.time() - START_COMMIT_TIME < 30:
            if self.current_auth_step:
                if self.current_auth_step == _steps.EnterCardNumber:
                    raise exceptions.CardNumberEnterRequired
                elif self.current_auth_step == _steps.EnterPassword:
                    raise exceptions.PasswordEnterRequired
                elif self.current_auth_step == _steps.EnterOtp:
                    raise exceptions.ReEnterOtp
                elif self.current_auth_step == _steps.CreatePin:
                    self._set_pin_code()

                    if self.current_auth_step is False:
                        return

        raise exceptions.AuthError

    def new_otp_code(self):
        WebDriverWait(self._driver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "#submit-form > div._Links_1jmjw_173._Links_center_1jmjw_1._Links_column_1jmjw_1 > button"),
            ),
        )

        new_otp_field = self._driver.find_element(
            "#submit-form > div._Links_1jmjw_173._Links_center_1jmjw_1._Links_column_1jmjw_1 > button"
        )

        new_otp_field.click()

    def enter_card_number(self, number: str):
        print("ENTER CARD")

        self._enter_card_number(number=number)

        print("ENTERED")

        try:
            print("SET PIN CODE")
            self._set_pin_code()
        except exceptions.PasswordSetRequired:
            print("NOPASSWORD")
            self._no_password()

        # try:
        #     WebDriverWait(self._driver, 20).until(
        #         expected_conditions.url(self._AUTHENTICATED_URL)
        #     )
        # except:
        #     self._driver.get(self._AUTHENTICATED_URL)
        #
        # print(self.authenticated)

    def pay_qr(self, path: str):
        self._driver.get("https://www.tbank.ru/mybank/payments/scan"
                          "/?internal_source=homePayments_qrCodeScan_open")

        try:
            WebDriverWait(self._driver, 30).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div/div/div/div[3]/main/div["
                               "2]/div/div/div/div/div/div/div[3]/div/div/input"),
                ),
            )
        except:
            browser.execute_script(
                '''
                window.open("https://www.tbank.ru/mybank/payments/scan"
                          "/?internal_source=homePayments_qrCodeScan_open","_blank");
                '''
            )

            WebDriverWait(self._driver, 30).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div/div/div/div[3]/main/div["
                               "2]/div/div/div/div/div/div/div[3]/div/div/input"),
                ),
            )

        file_upload = self._driver.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div/div[3]/main/div[2]/div/div/div/div/div/div/div[3]/div/div/input"
        )

        file_upload.send_keys(str(path))

        self._driver.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div/div[3]/main/div[2]/div/div/div/button"
        ).click()

        WebDriverWait(self._driver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div/div[3]/div/div/section/div/div[1]/div/form/div[4]/div[1]/button"),
            ),
        )

        self._driver.find_element(
            By.XPATH, "/html/body/div[1]/div/div[3]/div/div/section/div/div[1]/div/form/div[4]/div[1]/button"
        ).click()

    def no_password_way(self):
        if self.current_auth_step != _steps.EnterPassword:
            raise ValueError

        self._driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/main/div/div/div/form/div[2]/button"
        ).click()

        raise exceptions.CardNumberEnterRequired

    def _set_pin_code(self):
        WebDriverWait(self._driver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "#submit-form > div > div:nth-child(1) > div > div"),
            ),
        )

        code_fields = [
            "/html/body/div[1]/div/div/main/div/div/div/form/div/div["
            "1]/div/div/div[1]/input[1]",
            "/html/body/div[1]/div/div/main/div/div/div/form/div/div["
            "1]/div/div/div[1]/input[2]",
            "/html/body/div[1]/div/div/main/div/div/div/form/div/div["
            "1]/div/div/div[1]/input[3]",
            "/html/body/div[1]/div/div/main/div/div/div/form/div/div["
            "1]/div/div/div[1]/input[4]",
        ]

        WebDriverWait(self._driver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html/body/div[1]/div/div/main/div/div/div/form/div/div[1]/div/div/div[1]/input[1]"),
            ),
        )

        self._driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/main/div/div/div/form/div/div[1]/div/div/div[1]/input[1]"
        ).click()

        for i in range(len(self._DEFAULT_PIN)):
            self._driver.find_element(
                By.XPATH, code_fields[i]
            ).send_keys(self._DEFAULT_PIN[i])

        self._driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/main/div/div/div/form/div/div[2]/"
            "div/button[2]"
        ).click()

        raise exceptions.PasswordSetRequired

    def _no_password(self):
        WebDriverWait(self._driver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, "#submit-form > div > div:nth-child(3) > div > button._Button_az7dr_6._Button_flat_az7dr_1._Button_flat_size_l_az7dr_1"),
            ),
        )
        # submit-form > div > div:nth-child(3) > div > button._Button_az7dr_6._Button_flat_az7dr_1._Button_flat_size_l_az7dr_1
        # /html/body/div[1]/div/div/main/div/div/div/form/div/div[3]/div/button[1]
 # _Button_az7dr_6 _Button_flat_az7dr_1 _Button_flat_size_l_az7dr_1
        nopassword = self._driver.find_element(
            By.CSS_SELECTOR, "#submit-form > div > div:nth-child(3) > div > button._Button_az7dr_6._Button_flat_az7dr_1._Button_flat_size_l_az7dr_1"
        )

        nopassword.click()

    def _set_password(self):
        time.sleep(60)

        password = self._driver.find_element(
            By.XPATH, "/html/body/div[1]/div/div/main/div/"
            "div/div/form/div/div["
            "1]/div/div/label/input"
        )

        # password.click()

        password.send_keys(self._DEFAULT_PASS)

        time.sleep(60)

        self._driver.find_element(
            By.XPATH, "/html/body/div[1]/div/div/main/div/div/"
                      "div/form/div/div[3]/div/button[2]"
        ).click()

    def _enter_card_number(self, number: str):
        card_field = self._driver.find_element(
            By.XPATH, "/html/body/div[1]/div/div/main/div/div/div/form/div[1]/div/div/div/label/input"
        )

        card_field.click()

        card_field.send_keys(str(number))

        self._driver.find_element(
            By.CSS_SELECTOR,
            "#submit-form > div > div > div > button"
        ).click()

    def _enter_otp_code(self, code: str):
        WebDriverWait(self._driver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "#submit-form > div._Children_1jmjw_103 > div > div > div > label > input"),
            ),
        )

        otp_field = self._driver.find_element(
            By.CSS_SELECTOR, "#submit-form > div._Children_1jmjw_103 > div > "
                             "div > div > label > input"
        )

        otp_field.click()

        otp_field.send_keys(code)

    def _open_login_form(self):
        self._driver.get("https://tbank.ru/auth/login/")

        WebDriverWait(self._driver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "#submit-form > div > div > div > div > label > input"),
            ),
        )

        phone_input = self._driver.find_element(
            By.CSS_SELECTOR, "#submit-form > div > div > div > div > label > input"
        )

        phone_input.click()

        phone_input.send_keys(self._owner_phone)

        self._driver.find_element(
            By.CSS_SELECTOR,
            "#submit-form > div > div > div > button"
        ).click()
