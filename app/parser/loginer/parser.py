from selenium.webdriver.chrome.webdriver import ChromiumDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions


class PlatformLoginParser:
    _driver: ChromiumDriver

    def __init__(self, driver: ChromiumDriver):
        self._driver = driver

    def login(self, ref_link: str):
        self._open_login_form()
        self._set_phone_number()

    def _open_login_form(self):
        self._driver.get(ref_link)

        WebDriverWait(self._driver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "Button_button__aXkCB Button_primary__8vTWw Button_defaultSize__1RE37"),
            )
        )

        login_btn = self._driver.find_element(
            By.CLASS_NAME,
            "Button_button__aXkCB Button_primary__8vTWw Button_defaultSize__1RE37"
        )

        login_btn.click()

    def _set_phone_number(self):
        WebDriverWait(self._driver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html/body/div[1]/div/div[2]/div/main/div[2]/div/form/div[1]/div/input"),
            )
        )

        phone_field = self._driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div[2]/div/main/div[2]/div/form/div[1]/div/input"
        )

        phone_field.send_keys(...)
