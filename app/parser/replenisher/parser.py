import time

from selenium.webdriver import Chrome
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

from pathlib import Path

from .exceptions import ReplenishmentError


class AccountReplenishmentParser:
    _driver: Chrome
    _qr_path: str = None

    def __init__(self, driver: Chrome):
        self._driver = driver

    def get_payment_qr(self, account_phone: str):
        return self._get_qr(phone=self._format_phone(phone=account_phone))

    def wait_for_balance(self):
        self._driver.get("https://www.stoloto.ru/private/wallet?int=header")

        POLING_START = time.time()
        while time.time() - POLING_START < 10*60:
            WebDriverWait(self._driver, 60).until(
                expected_conditions.presence_of_element_located(
                    (By.CLASS_NAME, "WalletCard_balance__jIrWZ"),
                ),
            )

            try:
                if "10" in self._driver.find_element(
                    By.CLASS_NAME, "WalletCard_balance__jIrWZ"
                ).text:
                    return True
            except Exception as e:
                print(f"{e}")

            time.sleep(5)

            self._driver.execute_script("location.href = location.href;")

        return False

    def _get_qr(self, phone: str) -> str:
        self._driver.get("https://www.stoloto.ru/private/wallet/refill")

        self._driver.execute_script(
            """
            var css = '.flocktory-widget-overlay { display: none!important; }',
                head = document.head || document.getElementsByTagName('head')[0],
                style = document.createElement('style');
            
            head.appendChild(style);
            
            style.type = 'text/css';
            if (style.styleSheet){
              // This is required for IE8 and below.
              style.styleSheet.cssText = css;
            } else {
              style.appendChild(document.createTextNode(css));
            }        
            """
        )

        for _ in range(3):
            try:
                WebDriverWait(self._driver, 60).until(
                    expected_conditions.presence_of_element_located(
                        (By.CSS_SELECTOR, "body > sl-root > ng-component > main > div > ng-component > ng-component > uw-tabview > uw-tabpane:nth-child(2) > div > div > form > uw-form-group > uw-input > label > div.uw-input__body > input"),
                    ),
                )
            except:
                self._driver.execute_script("location.href = location.href")
        else:
            raise ReplenishmentError(
                "Error opening replenish form"
            )

        self._driver.find_element(
            By.CSS_SELECTOR, "body > sl-root > ng-component > main > div > ng-component > ng-component > uw-tabview > uw-tabpane:nth-child(2) > div > div > form > uw-form-group > uw-input > label > div.uw-input__body > input"
        ).send_keys(10)

        for _ in range(3):
            try:
                WebDriverWait(self._driver, 60).until(
                    expected_conditions.presence_of_element_located(
                        (By.CSS_SELECTOR, "body > sl-root > ng-component > main > "
                                          "div > ng-component > ng-component > uw-tabview > uw-tabpane:nth-child(2) > div > div > agent-constructor > form > div > div > uw-input > label > div.uw-input__body > input"),
                    ),
                )
                break
            except:
                self._driver.execute_script("location.href = location.href")
        else:
            raise ReplenishmentError("Error sending keys replenish form")

        phone_field = self._driver.find_element(
            By.CSS_SELECTOR, "body > sl-root > ng-component > main > div > ng-component > ng-component > uw-tabview > uw-tabpane:nth-child(2) > div > div > agent-constructor > form > div > div > uw-input > label > div.uw-input__body > input"
        )

        phone_field.click()

        phone_field.send_keys(phone)

        self._driver.find_element(
            By.CSS_SELECTOR, "body > sl-root > ng-component > main > div > ng-component > ng-component > uw-tabview > uw-tabpane:nth-child(2) > div > div > uw-form-group > uw-button > button"
        ).click()

        WebDriverWait(self._driver, 60).until(
            expected_conditions.presence_of_element_located(
                (By.TAG_NAME, "ngx-qrcode-styling"),
            ),
        )

        self._driver.find_element(
            By.TAG_NAME, "ngx-qrcode-styling"
        ).screenshot(
            self._generate_qr_path()
        )

        return self._qr_path

    def _generate_qr_path(self):
        if not self._qr_path:
            self._qr_path = str((
                Path(__file__).parent.parent.parent /
                f"static/qr-{time.time()}.png"
            ).absolute())

        return self._qr_path

    @staticmethod
    def _format_phone(phone: str) -> str:
        phone = phone.replace("+", "")
        if phone[0] != "9":
            phone = phone[1:]

        return phone
