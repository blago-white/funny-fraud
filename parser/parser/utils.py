import random
import time
from enum import Enum

from russian_names import RussianNames
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from .base import BaseParser


class OwnerCredentalsGenerator:
    @staticmethod
    def get_random_bd() -> str:
        return f"{str(random.randint(1, 28)).zfill(2)}{str(random.randint(1, 12)).zfill(2)}{random.randint(1982, 2006)}"

    @staticmethod
    def get_random_nick() -> str:
        p = RussianNames().get_person(patronymic=False, transliterate=True).split(" ")

        nick = p[0][:random.randint(2, len(p[0]))+1], p[1][:random.randint(3, len(p[1]))]

        if random.randint(0, 1) == 1:
            nick = tuple([
                (i.lower() if random.randint(0, 1) == 1 else i)
                for i in nick
            ])

        nick = random.choice(["_", "", "-", "", "", "2", "4", "-", "-", ""]).join(nick)

        if random.randint(0, 10) == 1:
            nick += str(random.randint(0, 99))
        else:
            if random.randint(0, 6) == 1:
                nick += str(random.randint(1980, 2006))

        return nick


class CheapStolotoGames(Enum):
    DVADVA_20 = "https://www.stoloto.ru/dvazhdydva/game"
    SLADKI_15 = "https://www.stoloto.ru/ostatki-sladki/game"
    UDACHA_30 = "https://www.stoloto.ru/udachanasdachu/game"
    RAPIDO2_50 = "https://www.stoloto.ru/rapido2/game"


class ExpensiveStolotoGames(Enum):
    FZP_100 = "https://www.stoloto.ru/fzp/game"


class TicketBuyer(BaseParser):
    _METHOD_BY_GAME = {
        ExpensiveStolotoGames.FZP_100: "_select_fzp",
        CheapStolotoGames.DVADVA_20: "_select_dvadva",
        CheapStolotoGames.SLADKI_15: "_select_ostatki_sladki",
        CheapStolotoGames.UDACHA_30: "_select_udacha_na_sdachu",
        CheapStolotoGames.RAPIDO2_50: "_select_rapido2",
    }

    def __init__(self, driver: WebDriver):
        self._driver = driver

    def order_ticket(self, ticket_recipient_phone: str):
        """
        This method do:

        1. Open page with game
        2. Select ticket
        3. Enter recipient phone
        4. Click "Buy" button

        :param ticket_recipient_phone: Phone, started with 9..., e.g. 999-333-22-44
        """

        self.select_ticket()

        time.sleep(1)

        self._wait_for_element(
            By.CSS_SELECTOR, 'input[data-test-id="gift-btn"]'
        ).click()

        time.sleep(1)

        recipient_phone_input = self._wait_for_element(
            By.CSS_SELECTOR, 'input[data-test-id="gift-phone"]'
        )

        time.sleep(1)

        recipient_phone_input.send_keys(ticket_recipient_phone)

        time.sleep(1)

        self._wait_for_element(
            By.CSS_SELECTOR, 'button[data-test-id="sbp"]'
        ).click()

    def select_ticket(self):
        link = self.get_link()

        driver.get(url=link.value)

        self.select_ticket_on_page(game=link)

    def get_link(self) -> CheapStolotoGames | ExpensiveStolotoGames:
        if random.randint(0, 10) <= 2:
            return random.choice(list(ExpensiveStolotoGames))

        return random.choice(list(CheapStolotoGames))

    def select_ticket_on_page(
            self, game: ExpensiveStolotoGames | CheapStolotoGames
    ):
        self.__getattribute__(self._METHOD_BY_GAME[game])(self)

    def _select_fzp(self):
        self._wait_for_element(
            By.CLASS_NAME, "Ticket_btn__1NSeH Ticket_montserrat__4wFhQ", 60
        ).click()

    def _select_dvadva(self):
        self._wait_for_element(
            By.CSS_SELECTOR, 'button[data-test-id="randombtn"]', 60
        ).click()

    def _select_ostatki_sladki(self):
        self._wait_for_element(
            By.CLASS_NAME, 'button[data-test-id="ticket"]', 60
        ).click()

    def _select_udacha_na_sdachu(self):
        self._wait_for_element(
            By.CLASS_NAME, "TicketTemplate_udachaNaSdachuTicketTemplate__tV_eh", 60
        ).click()

    def _select_rapido2(self):
        self._wait_for_element(
            By.CSS_SELECTOR, 'button[data-test-id="randombtn"]', 60
        ).click()
