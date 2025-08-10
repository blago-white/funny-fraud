import time
from pathlib import Path
import selenium.webdriver.remote.webelement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome

from db.transfer import AccountMailCredentials

from ..captcha.capguru import CapGuruApiAdapter
from ..captcha.base import BaseCaptchaSolverAPIAdapter
from ..captcha.data import CaptchaClickType

from . import utils


class StolotoTicketsParser:
    _captcha_solver: BaseCaptchaSolverAPIAdapter

    _form_already_inited: bool = False

    _AFTER_ENTERING_PHONE_PAGE_URL = "https://www.stoloto.ru/auth/login?from=reg_phone"
    _START_LOGINING_PAGE_URL = "https://www.stoloto.ru/auth"

    def __init__(
            self, driver: Chrome,
            owner_data_generator: utils.OwnerCredentalsGenerator = None,
            captcha_solver_adapter: CapGuruApiAdapter = CapGuruApiAdapter):
        self._driver = driver

        self._owner_data_generator = (owner_data_generator or
                                      utils.OwnerCredentalsGenerator())

        self._captcha_solver = captcha_solver_adapter()

    def open_registration_form(self, url: str):
        if not self._form_already_inited:
            self._driver.get(url=url)

            print("CLICK START REGISTER BUTTON")

            self._click_start_register_button()

            print("START CHECK LOGIN FORM LOADED")

            self._check_login_form_loaded()

            print("CHECKED LOGIN FORM")

            self._form_already_inited = True
        else:
            try:
                self._drop_reg_form()
            except:
                raise ValueError("Cannot drop form")
            else:
                return

    def register_phone(self, phone: str):
        print("START ENTERING PHONE")

        self._enter_phone(phone=phone)

        print("START CLICKING CAPTCHA")

        self._pass_captcha_challenge()

        print("SUBMITING")

        self._submit_reg_phone_form()

    def enter_reg_sms_code(self, code: str):
        ...

    def continue_registration(self, mail: AccountMailCredentials):
        ...

    def buy_ticket(self):
        ...

    def _submit_reg_phone_form(self):
        self._driver.find_element(
            By.ID, "otp-1"
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
        else:
            raise ValueError("Otp fields not loaded after 120 sec.")

    def _pass_captcha_challenge(self):
        WebDriverWait(self._driver, 30).until(
            expected_conditions.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@title="reCAPTCHA"]'))
        )

        # captcha = self._driver.find_element(
        #     By.XPATH, '//iframe[@title="reCAPTCHA"]'
        # )
        #
        # self._driver.switch_to.frame(captcha)

        checkbox = self._wait_for_element(
            by='id',
            locator='recaptcha-anchor',
        )

        self._js_click(checkbox)

        if checkbox.get_attribute('aria-checked') == 'true':
            return

        self._driver.switch_to.parent_frame()

        captcha = self._wait_for_element(
            by=By.XPATH,
            locator='/html/body/div[4]/div[4]/iframe',
        )

        self._driver.switch_to.frame(captcha)

        try:
            WebDriverWait(self._driver, 30).until(
                expected_conditions.presence_of_element_located((By.ID, "rc-imageselect"))
            )
        except:
            print(self._driver.page_source)

        self._driver.find_element(By.ID, "rc-imageselect").screenshot(filename="D:\FDISKCOPY\python\stoloto\screenshot.png")
        instruction = self._driver.find_element(By.CLASS_NAME, "rc-imageselect-desc").find_element(By.TAG_NAME, "strong").text

        solve_coordinates = self._captcha_solver.solve_captcha(
            captcha_photo_path="D:\FDISKCOPY\python\stoloto\screenshot.png",
            text_instruction=instruction.lower(),
        )

        self._driver.switch_to.parent_frame()

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

        self._driver.fullscreen_window()

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

    def _drop_reg_form(self):
        if self._driver.current_url != self._AFTER_ENTERING_PHONE_PAGE_URL:
            if self._driver.current_url == self._START_LOGINING_PAGE_URL:
                return

            raise ValueError("Cannot revert form!")

        self._driver.navigate().back()

        for _ in range(2):
            try:
                self._check_login_form_loaded()
                break
            except:
                pass

    def _wait_for_element(
        self,
        by: str = By.ID,
        locator: str | None = None,
        timeout: float = 10,
    ) -> selenium.webdriver.remote.webelement.WebElement:
        """
        Try to locate web element within given duration.

        :param by: strategy to use to locate element (see class `selenium.webdriver.common.by.By`)
        :param locator: locator that identifies the element
        :param timeout: number of seconds to wait for element before raising `TimeoutError`
        :return: located web element
        :raises selenium.common.exceptions.TimeoutException: if element is not located within given duration
        """

        return WebDriverWait(self._driver, timeout).until(expected_conditions.presence_of_element_located((by, locator)))

    def _js_click(self, element: WebElement) -> None:
        """
        Perform click on given web element using JavaScript.

        :param element: web element to click
        """

        self._driver.execute_script('arguments[0].click();', element)
