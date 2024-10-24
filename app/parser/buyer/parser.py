import time

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from . import exceptions


class AccountTicketsService:
    def __init__(self, driver: Chrome,
                 ticket_path: str = "https://www.stoloto.ru/rapido-drive/game?int=left"):
        self._ticket_path = ticket_path
        self._driver = driver

    def buy(self):
        for _ in range(3):
            self._driver.get(self._ticket_path)

            print("OPENING")

            try:
                print("WAIT")

                self._driver.execute_script(
                    """                    
                    document.querySelectorAll(
                        '[data-test-id="randombtn"]'
                    )[0].id = "randomTargetBtn";

                    document.getElementById('randomTargetBtn').style.transform = "scale(10)";

                    document.getElementById('randomTargetBtn').style.zIndex = 100000;
                    """
                )

                print("FIND")
                self._driver.find_element(
                    By.ID, "randomTargetBtn"
                ).click()
                print("CLICK")
                break
            except Exception as e:
                print("ERROR", e)
                time.sleep(60)
                pass
                # //*[@id="__next"]/div/div[2]/div/main/div[2]/div[2]/div/div/div[2]/div/div/div[2]/button
        else:
            # /html/body/div[1]/div/div[2]/div/main/div[2]/div[2]/div/div/div[2]/div/div/div[2]/button
            raise exceptions.TicketBuyFail

        print("FIND2")
        WebDriverWait(self._driver, 60).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "#__next > div.RootLayout_layout__AN70W > "
                 "div.Wrap_wrap__YsCW8.Wrap_wrap__mYUid.PageLayout_wrap__bHTtx > div > main > div.Game_game__rLn16 > div.GameContentContainer_gameContentContainer__T_6t1 > aside > div > div.SidebarContainer_sidebarContainer__tw5FC.SidebarContainer_checkout__tIFrB > div > div.Checkout_checkoutActions__L137d > div > button.Button_button__aXkCB.Button_fluid__2K933.Button_defaultSize__1RE37.ButtonGame_robotoFlex___PuFe.ButtonGame_gameBtn__WoYPN.ButtonGame_primary__hoaO2.Purchase_paymentBtn__zXkpz.Purchase_purchase__QEgWe")

            )
        )

        self._driver.find_element(
            By.CSS_SELECTOR,
                 "#__next > div.RootLayout_layout__AN70W > "
                 "div.Wrap_wrap__YsCW8.Wrap_wrap__mYUid.PageLayout_wrap__bHTtx > div > main > div.Game_game__rLn16 > div.GameContentContainer_gameContentContainer__T_6t1 > aside > div > div.SidebarContainer_sidebarContainer__tw5FC.SidebarContainer_checkout__tIFrB > div > div.Checkout_checkoutActions__L137d > div > button.Button_button__aXkCB.Button_fluid__2K933.Button_defaultSize__1RE37.ButtonGame_robotoFlex___PuFe.ButtonGame_gameBtn__WoYPN.ButtonGame_primary__hoaO2.Purchase_paymentBtn__zXkpz.Purchase_purchase__QEgWe"
        ).click()
