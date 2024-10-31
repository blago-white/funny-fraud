import time

from pathlib import Path

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from . import exceptions


class AccountTicketsService:
    _qr_path = ""

    def __init__(self, driver: Chrome,
                 ticket_path: str = "https://www.stoloto.ru/zabava/game?int=left"):
        self._ticket_path = ticket_path
        self._driver = driver

    def get_qr(self) -> str:
        for _ in range(5):
            self._driver.get(self._ticket_path)

            print("OPENING")

            try:
                print("WAIT")

                WebDriverWait(self._driver, 60).until(
                    expected_conditions.presence_of_element_located(
                        (By.CLASS_NAME,
                        'ButtonRandom_btnRandom__q7SkB')
                    )
                )

                self._driver.execute_script(
                    """                 
                    
                    const elem = document.querySelectorAll('[data-test-id="randombtn"]')[0]
                    
                    elem.id = "randomTargetBtn";
                    
                    document.getElementById(
                        'randomTargetBtn'
                    ).style.transform = "scale(1.1)";

                    document.getElementById('randomTargetBtn').style.zIndex = 100000;
                    
                    document.getElementById(
                        'randomTargetBtn'
                    ).style.position = 'absolute';
                    
                    const overlay = document.getElementById('layers');
                    
                    if (overlay) {
                        overlay.style.display = 'none'
                    }
                    """
                )

                print("FIND")
                rand_btn = self._driver.find_element(
                    By.ID, "randomTargetBtn"
                )
                print(f"FIND {rand_btn}")

                try:
                    rand_btn.click()
                except:
                    WebDriverWait(self._driver, 20).until(
                        expected_conditions.presence_of_element_located(
                            (By.ID, 'layers')
                        )
                    )

                    self._driver.execute_script("""
                        const overlay = document.getElementById('layers');
                        
                        if (overlay) {
                            overlay.style.display = 'none'
                        }
                    """)

                    rand_btn.click()

                print("CLICK")

                print("FIND2")
                WebDriverWait(self._driver, 60).until(
                    expected_conditions.element_to_be_clickable(
                        (By.XPATH,
                         "/html/body/div[1]/div[2]/div[2]/div/main/div[2]/div[3]/aside/div/div[2]/div/div[5]/div/button[1]")

                    )
                )

                self._driver.find_element(
                    By.XPATH,
                         "/html/body/div[1]/div[2]/div[2]/div/main/div[2]/div[3]/aside/div/div[2]/div/div[5]/div/button[1]"
                ).click()

                WebDriverWait(self._driver, 60).until(
                    expected_conditions.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         "body > aside > div > div > div.Sbp_content__uNOOd > img")

                    )
                )

                print("QR")

                return self._make_screenshot(elem=self._driver.find_element(
                    By.CSS_SELECTOR,
                    "body > aside > div > div > div.Sbp_content__uNOOd > img"
                ))
            except Exception as e:
                print("ERROR", e)
                pass
        else:
            raise exceptions.TicketBuyFail

    def _make_screenshot(self, elem):
        print(self._generate_qr_path())

        elem.screenshot(self._qr_path)

        return self._qr_path

    def _generate_qr_path(self):
        if not self._qr_path:
            self._qr_path = str((
                Path(__file__).parent.parent.parent /
                f"static/qr-{time.time()}.png"
            ).absolute())

        return self._qr_path
