import os
import random
import time
from pathlib import Path
import selenium.webdriver.remote.webelement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains

from db.transfer import AccountMailCredentials

from ..captcha.capguru import CapGuruApiAdapter
from ..captcha.base import BaseCaptchaSolverAPIAdapter
from ..captcha.data import CaptchaClickType

from . import utils


def _delete_captcha_img(path: str):
    try:
        os.remove(path=path)
    except:
        print("CANNOT DELETE CAPTCHA IMAGE!")
        pass


class StolotoTicketsParser:
    _captcha_solver: BaseCaptchaSolverAPIAdapter

    _form_already_inited: bool = False

    _AFTER_ENTERING_PHONE_PAGE_URLS = ["https://www.stoloto.ru/auth/login?from=reg_phone", "https://www.stoloto.ru/auth/registration-push-sms?from=reg_phone"]
    _START_LOGINING_PAGE_URL = "https://www.stoloto.ru/auth"
    _CAPTCHA_SCREENSHOTS_PATH_TEMP = "D:\\FDISKCOPY\\python\\stoloto\\screenshot-{r}.png"

    _CAPTCHA_TRIES_COUNT = 50

    def __init__(
            self, driver: Chrome,
            owner_data_generator: utils.OwnerCredentalsGenerator = None,
            captcha_solver_adapter: CapGuruApiAdapter = CapGuruApiAdapter):
        self._driver = driver

        self._owner_data_generator = (owner_data_generator or
                                      utils.OwnerCredentalsGenerator())

        self._captcha_solver = captcha_solver_adapter()

    def open_registration_form(self, url: str):
        self._driver.fullscreen_window()

        self._driver.get(url=url)

        print("CLICK START REGISTER BUTTON")

        self._driver.fullscreen_window()

        self._click_start_register_button()

        print("START CHECK LOGIN FORM LOADED")

        self._check_login_form_loaded()

        print("CHECKED LOGIN FORM")

        self._form_already_inited = True

    def register_phone(self, phone: str):
        print("START ENTERING PHONE")

        self._enter_phone(phone=phone)

        print("START CLICKING CAPTCHA")

        self._pass_captcha_challenge()

        print("SUBMITING")

        self._submit_reg_phone_form()

    def enter_reg_sms_code(self, code: str, _recursion_n: int = 0):
        if _recursion_n > 5:
            raise Exception("Cannot send otp code!")

        for idx, dig in enumerate(code, start=1):
            dig_input = self._driver.find_element(By.ID, f"otp-{idx}")

            dig_input.click()

            time.sleep(.1)

            dig_input.send_keys(dig)

            time.sleep(.5)

        time.sleep(2)

        if "возникла техническая ошибка. пожалуйста, попробуйте позже" in self._driver.page_source.lower():
            self._driver.back()

            time.sleep(10)

            self._wait_for_element(By.ID, "otp-1")

            try:
                self._driver.find_element(By.ID, "otp-1")
            except:
                self._wait_for_element(By.ID, "otp-1")

            return self.enter_reg_sms_code(code=code, _recursion_n=_recursion_n+1)

        try:
            self._wait_for_main_header_change(text_in="Регистрация")
        except:
            return self.enter_reg_sms_code(code=code, _recursion_n=_recursion_n+1)

    def continue_registration(self, mail: AccountMailCredentials):
        try:
            self._wait_for_main_header_change(text_in="Регистрация")
        except:
            raise Exception("Cannot register!")

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
            raise Exception("Registered, buy problems with URL!")

        print("!!! REGISTRATED SUCCESSFULLY !!!")

    def buy_ticket(self):
        ...

    def check_number_not_blocked(self):
        if "не удалось подтвердить номер" in self._driver.page_source.lower():
            raise Exception("Number blocked!")

    def _submit_reg_phone_form(self):
        self._driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        for _ in range(20):
            try:
                WebDriverWait(self._driver, 6).until(
                    expected_conditions.presence_of_element_located(
                        (By.ID, "otp-1")
                    )
                )
            except:
                pass

            if "Забыли пароль?" in self._driver.page_source:
                raise ValueError("Phone number already registered!")

            break
        else:
            raise ValueError("Otp fields not loaded after 120 sec.")

    def _pass_captcha_challenge(self):
        if self._try_pass_captcha_using_click():
            return

        self._switch_to_captcha_body()

        try:
            WebDriverWait(self._driver, 30).until(
                expected_conditions.presence_of_element_located((By.ID, "rc-imageselect"))
            )
        except:
            self._driver.switch_to.parent_frame()
            return

        captcha_img_path = self._CAPTCHA_SCREENSHOTS_PATH_TEMP.format(r=random.randint(0, 1000))

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
                self._js_click(
                    self._driver.find_element(
                        By.CSS_SELECTOR,
                        f'td[tabindex="{tile_number+3}"]'
                    )
                )

                time.sleep(.5)

            self._js_click(
                self._driver.find_element(By.ID, "recaptcha-verify-button")
            )

            time.sleep(1)

            if self._check_captcha_passed():
                self._driver.switch_to.parent_frame()

                _delete_captcha_img(path=captcha_img_path)

                return

            self._switch_to_captcha_body()

        _delete_captcha_img(path=captcha_img_path)

        raise Exception("UNSOLVABLE CAPTCHA!")

    def _try_pass_captcha_using_click(self) -> bool:
        WebDriverWait(self._driver, 30).until(
            expected_conditions.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@title="reCAPTCHA"]'))
        )

        checkbox = self._wait_for_element(
            by='id',
            locator='recaptcha-anchor',
        )

        self._js_click(checkbox)

        if checkbox.get_attribute('aria-checked') == 'true':
            self._driver.switch_to.parent_frame()
            return True

        self._driver.switch_to.parent_frame()

        return False

    def _enter_phone(self, phone: str):
        WebDriverWait(self._driver, 40).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[inputmode="tel"]')
            )
        )

        phone_input = self._wait_for_element(
            By.CSS_SELECTOR,
            'input[inputmode="tel"]'
        )

        phone_input.click()

        time.sleep(.5)

        phone_input.send_keys(phone)

    def _click_start_register_button(self):
        try:
            WebDriverWait(self._driver, 40).until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, 'a[href="/auth"]')
                )
            )
        except:
            raise exceptions.TraficBannedError()

        self._driver.find_element(
            By.CSS_SELECTOR, 'a[href="/auth"]'
        ).click()

    def _check_login_form_loaded(self):
        try:
            WebDriverWait(self._driver, 40).until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[inputmode="tel"]')
                )
            )
        except:
            raise exceptions.TraficBannedError()

        try:
            WebDriverWait(self._driver, 60).until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, 'iframe[title="reCAPTCHA"]')
                )
            )
        except:
            raise exceptions.TraficBannedError()

    def drop_reg_form(self):
        if self._driver.current_url == self._START_LOGINING_PAGE_URL:
            return

        self._driver.back()

        for _ in range(2):
            try:
                self._check_login_form_loaded()
                break
            except:
                pass

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

    def _wait_for_main_header_change(self, text_in: str, timeout: float = 60):
        START = time.time()

        while (time.time() - START) < timeout:
            try:
                if text_in.lower() in self._driver.find_element(By.TAG_NAME, "h1").text.lower():
                    return
            except:
                pass

            time.sleep(1)

        raise Exception("Header not changed!")

    def _wait_for_element(
        self,
        by: str = By.ID,
        locator: str | None = None,
        timeout: float = 10,
    ) -> selenium.webdriver.remote.webelement.WebElement:
        return WebDriverWait(self._driver, timeout).until(expected_conditions.presence_of_element_located((by, locator)))

    def _js_click(self, element: WebElement) -> None:
        self._driver.execute_script('arguments[0].click();', element)
