import os
import random
import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome

from db.transfer import AccountMailCredentials
from . import base
from . import utils
from . import exceptions
from ..captcha.base import BaseCaptchaSolverAPIAdapter
from ..captcha.capguru import CapGuruApiAdapter


class StolotoTicketsParser(base.BaseParser):
    _captcha_solver: BaseCaptchaSolverAPIAdapter

    _AFTER_ENTERING_PHONE_PAGE_URLS = ["https://www.stoloto.ru/auth/login?from=reg_phone", "https://www.stoloto.ru/auth/registration-push-sms?from=reg_phone"]
    _START_LOGINING_PAGE_URL = "https://www.stoloto.ru/auth"
    _CAPTCHA_SCREENSHOTS_PATH_TEMP = "D:\\FDISKCOPY\\python\\stoloto\\screenshot-{r}.png"
    _TICKETS_PAYMENT_QRS_SCREENSHOTS_DIR = str((Path(__file__).parent.parent.parent / "data/tickets-qrs").absolute())

    _CAPTCHA_TRIES_COUNT = 50

    def __init__(
            self, driver: Chrome,
            session_id: int,
            lead_id: int,
            owner_data_generator: utils.OwnerCredentalsGenerator = utils.OwnerCredentalsGenerator,
            captcha_solver_adapter: CapGuruApiAdapter = CapGuruApiAdapter,
            ticket_buyer: utils.TicketBuyer = utils.TicketBuyer):
        self._driver = driver

        self._session_id = session_id
        self._lead_id = lead_id

        self._owner_data_generator = owner_data_generator()
        self._captcha_solver = captcha_solver_adapter()
        self._ticket_buyer = ticket_buyer(driver=driver)

    def open_registration_form(self, url: str):
        self._driver.maximize_window()

        self._driver.get(url=url)

        print("CLICK START REGISTER BUTTON")

        self._driver.maximize_window()

        self._click_start_register_button()

        print("START CHECK LOGIN FORM LOADED")

        self._check_login_form_loaded()

        print("CHECKED LOGIN FORM")

    def register_phone(self, phone: str):
        print("START ENTERING PHONE")

        self._enter_phone(phone=phone)

        print("START CLICKING CAPTCHA")

        self._pass_captcha_challenge()

        print("SUBMITING")

        self._submit_reg_phone_form()

    def enter_reg_sms_code(self, code: str, _recursion_n: int = 0):
        if _recursion_n > 5:
            raise exceptions.RegOtpEnteringError("Cannot enter otp code!")

        for idx, dig in enumerate(code, start=1):
            dig_input = self._driver.find_element(By.ID, f"otp-{idx}")

            dig_input.click()

            time.sleep(.1)

            dig_input.send_keys(dig)

            time.sleep(.5)

        time.sleep(2)

        if "возникла техническая ошибка. пожалуйста, попробуйте позже" in self._driver.page_source.lower():
            self._driver.back()

            self._wait_for_element(By.ID, "otp-1", 45)

            try:
                self._driver.find_element(By.ID, "otp-1")
            except:
                self._wait_for_element(By.ID, "otp-1")

            return self.enter_reg_sms_code(code=code, _recursion_n=_recursion_n+1)

        try:
            self._check_main_header_contains(text_in="Регистрация")
        except:
            return self.enter_reg_sms_code(code=code, _recursion_n=_recursion_n+1)

    def continue_registration(self, mail: AccountMailCredentials):
        try:
            self._check_main_header_contains(text_in="Регистрация")
        except:
            raise exceptions.AccountRegistrationPageError("Cannot register!")

        mail_input = self._wait_for_element(
            By.CSS_SELECTOR,
            'input[inputmode="email"]',
            timeout=30
        )
        password_input = self._wait_for_element(
            By.CSS_SELECTOR,
            'input[name="user_password"]',
            timeout=30
        )

        time.sleep(1)

        mail_input.click()

        time.sleep(.5)

        mail_input.send_keys(mail.addr)

        time.sleep(1)

        password_input.click()

        time.sleep(.5)

        password_input.send_keys(mail.password)

        time.sleep(1)

        self._driver.find_element(
            By.CSS_SELECTOR,
            'button[type="submit"]'
        ).click()

        try:
            WebDriverWait(self._driver, 60).until(
                expected_conditions.url_contains("complete")
            )
        except:
            raise exceptions.AccountRegistrationPageWarning(
                "Registered, but problems with URL!"
            )

        print("!!! REGISTRATED SUCCESSFULLY !!!")

    def fill_profile_data(self):
        self._driver.get("https://www.stoloto.ru/private/data?int=lkmain")

        display_name_input = self._wait_for_element(By.CSS_SELECTOR, 'input[name="displayName"]', 30)

        display_name_input.click()

        time.sleep(.5)

        display_name_input.send_keys(self._owner_data_generator.get_random_nick())

        bd_input = self._wait_for_element(By.CSS_SELECTOR, 'input[name="birthDate"]', 30)

        bd_input.click()

        time.sleep(.5)

        bd_input.send_keys(self._owner_data_generator.get_random_bd())

        self._driver.find_element(By.CLASS_NAME, "Button_button__aXkCB Button_primary__8vTWw Button_fluid__2K933 Button_defaultSize__1RE37")

    def buy_ticket(self, ticket_recipient_phone: str) -> str:
        """
        Image of QR for payment saved by path: stoloto/data/tickets-qrs/{session_id}-{lead_id}.png

        :param ticket_recipient_phone: Phone of ticket's recipient
        :return: Path to payment qr screenshot
        """
        self._ticket_buyer.order_ticket(
            ticket_recipient_phone=ticket_recipient_phone
        )

        qr_saving_path = self._get_ticket_qr_saving_path()

        self._wait_for_element(
            By.CLASS_NAME, "Sbp_container__A0Jah"
        ).screenshot(
            filename=qr_saving_path
        )

        return qr_saving_path

    def check_number_not_blocked(self, raise_exception: bool = True) -> bool:
        if "не удалось подтвердить номер" in self._driver.page_source.lower():
            if raise_exception:
                raise exceptions.NumberBlockedByStolotoError("Number blocked!")
            return False
        return True

    def drop_reg_form(self):
        if self._driver.current_url == self._START_LOGINING_PAGE_URL:
            return

        self._driver.back()

    def _submit_reg_phone_form(self):
        self._driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        for _ in range(20):
            try:
                self._wait_for_element(By.ID, "otp-1", 6)
            except:
                pass

            if "Забыли пароль?" in self._driver.page_source:
                raise exceptions.PhoneAlreadyRegisteredError(
                    "Phone number already registered!"
                )

            break
        else:
            raise TimeoutError("Otp fields not loaded after 120 sec.")

    def _pass_captcha_challenge(self):
        if self._try_pass_captcha_using_click():
            return

        self._solve_captcha()

        raise exceptions.UnsolvableCaptchaError("UNSOLVABLE CAPTCHA!")

    def _solve_captcha(self):
        self._switch_to_captcha_body()

        try:
            self._wait_for_element(By.ID, "rc-imageselect", 30)
        except:
            return self._driver.switch_to.parent_frame()

        captcha_img_path = self._CAPTCHA_SCREENSHOTS_PATH_TEMP.format(
            r=random.randint(0, 1000)
        )

        for _ in range(self._CAPTCHA_TRIES_COUNT):
            if _ > 0:
                time.sleep(1)

            print(f"CAPTCHA TRY N{_}")

            if ("когда изображения закончатся" in self._driver.page_source.lower()
                    or "once there are none left" in self._driver.page_source.lower()):
                print("Calnceled bad challenge SKIPED")

                self._driver.find_element(By.ID, "recaptcha-reload-button").click()
                continue

            captcha = self._driver.find_element(By.ID, "rc-imageselect")
            captcha.screenshot(filename=captcha_img_path)

            try:
                instruction = self._driver.find_element(By.CLASS_NAME, "rc-imageselect-desc").text
            except:
                instruction = self._driver.find_element(By.CLASS_NAME, "rc-imageselect-desc-no-canonical").text

            try:
                solve = self._captcha_solver.solve_captcha(
                    captcha_photo_path=captcha_img_path,
                    text_instruction=instruction,
                )
            except:
                self._driver.find_element(By.ID, "recaptcha-reload-button").click()
                continue

            for tile_number in solve:
                self._make_js_click(
                    self._driver.find_element(
                        By.CSS_SELECTOR,
                        f'td[tabindex="{tile_number+3}"]'
                    )
                )

                time.sleep(.5)

            self._make_js_click(
                self._driver.find_element(By.ID, "recaptcha-verify-button")
            )

            time.sleep(1)

            if self._check_captcha_passed():
                self._driver.switch_to.parent_frame()

                utils.delete_captcha_img(path=captcha_img_path)

                return

            self._switch_to_captcha_body()

        utils.delete_captcha_img(path=captcha_img_path)

    def _try_pass_captcha_using_click(self) -> bool | None:
        WebDriverWait(self._driver, 30).until(
            expected_conditions.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@title="reCAPTCHA"]'))
        )

        checkbox = self._wait_for_element(
            by='id',
            locator='recaptcha-anchor',
        )

        self._make_js_click(checkbox)

        if checkbox.get_attribute('aria-checked') == 'true':
            self._driver.switch_to.parent_frame()
            return True

        self._driver.switch_to.parent_frame()

    def _enter_phone(self, phone: str):
        phone_input = self._wait_for_element(By.CSS_SELECTOR, 'input[inputmode="tel"]', 40)

        phone_input.click()

        time.sleep(.5)

        phone_input.send_keys(phone)

    def _click_start_register_button(self):
        try:
            self._wait_for_element(By.CSS_SELECTOR,
                                   'a[href="/auth"]',
                                   40)
        except:
            raise exceptions.TraficBannedError()

        self._driver.find_element(
            By.CSS_SELECTOR, 'a[href="/auth"]'
        ).click()

    def _check_login_form_loaded(self):
        try:
            self._wait_for_element(By.CSS_SELECTOR, 'input[inputmode="tel"]', 40)
        except:
            raise exceptions.TraficBannedError()

        try:
            self._wait_for_element(By.CSS_SELECTOR, 'iframe[title="reCAPTCHA"]', 60)
        except:
            raise exceptions.TraficBannedError()

    def _check_captcha_passed(self):
        self._driver.switch_to.parent_frame()

        WebDriverWait(self._driver, 30).until(
            expected_conditions.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@title="reCAPTCHA"]'))
        )

        checkbox = self._wait_for_element(
            by='id',
            locator='recaptcha-anchor',
        )

        if checkbox.get_attribute('aria-checked') == 'true':
            return True

        self._driver.switch_to.parent_frame()

    def _switch_to_captcha_body(self):
        captcha = self._wait_for_element(
            by=By.XPATH,
            locator='/html/body/div[4]/div[4]/iframe',
        )

        self._driver.switch_to.frame(captcha)

    def _check_main_header_contains(self, text_in: str, timeout: float = 60):
        START = time.time()

        while (time.time() - START) < timeout:
            try:
                if text_in.lower() in self._driver.find_element(By.TAG_NAME, "h1").text.lower():
                    return
            except:
                pass

            time.sleep(1)

        raise exceptions.PageHeaderNotChangedError("Header not changed!")

    def _get_ticket_qr_saving_path(self) -> str:
        return (self._TICKETS_PAYMENT_QRS_SCREENSHOTS_DIR +
                f"\\{self._session_id}-{self._lead_id}.png")
