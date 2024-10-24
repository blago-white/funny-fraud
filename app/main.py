import asyncio
import time

import redis
import dotenv

dotenv.load_dotenv()

from db.services.sessions import SessionsService
from db.services.banking import BotBankingStatusService
from parser.drivers import WebDriversService
from parser.banking.parser import BaseBankingParser
from parser.buyer.parser import AccountTicketsService


async def main():
    b = AccountTicketsService(
        driver=await WebDriversService().get()
    )

    for _ in range(10):
        print(_*10)
        time.sleep(10)

    b.buy()

    # from bot.main import startup

    # conn = redis.Redis.from_url("redis://localhost:6379/0")
    #
    # SessionsService(conn=conn)
    #
    # BotBankingStatusService(conn=conn)
    #
    # BaseBankingParser(driver=await WebDriversService().get())
    #
    # await startup()





    # p = BaseBankingParser(owner_phone="9952481751",
    #                       driver=await WebDriversService().get())
    #
    # p.send_login_request()
    #
    # code = input("Enter sms code: ")
    #
    # try:
    #     p.enter_otp_code(code=code)
    # except CardNumberEnterRequired:
    #     card = input("Enter card: ")
    #
    #     p.enter_card_number(number=card)
    # except PasswordEnterRequired:
    #     try:
    #         p.no_password_way()
    #     except CardNumberEnterRequired:
    #         card = input("Enter card: ")
    #
    #         p.enter_card_number(number=card)
    #
    # print(f"AUTHENTICATED: {p.authenticated}")
    #
    # pl = PlatformLeadsService(
    #     payments_service=p,
    # )
    #
    # await pl.generate()

    # #__next > div > div.Wrap_wrap__YsCW8.Wrap_wrap__mYUid.PageLayout_wrap__bHTtx > div > main > div > div.Container_container__2bu_W > h1

    # driver = await WebDriversService().get()
    #
    # a = AccountReplenishmentParser(driver=driver)
    #
    # time.sleep(200)
    #
    # print(a.get_payment_qr("89952481751"))

    # print(driver)
    #
    # p = PlatformLoginParser(
    #     driver=driver
    # )

    # await p.login(ref_link="https://www.stoloto.ru/")

    # time.sleep(6000)

    # p = BaseBankingParser(owner_phone="9952481751",
    #                       driver=WebDriversService().get())
    #
    # p.send_login_request()
    #
    # code = input("Enter sms code: ")
    #
    # try:
    #     p.enter_otp_code(code=code)
    # except CardNumberEnterRequired:
    #     card = input("Enter card: ")
    #
    #     p.enter_card_number(number=card)
    # except PasswordEnterRequired:
    #     try:
    #         p.no_password_way()
    #     except CardNumberEnterRequired:
    #         card = input("Enter card: ")
    #
    #         p.enter_card_number(number=card)
    #
    # print(f"AUTHENTICATED: {p.authenticated}")
    #
    # p.pay_qr(str((Path(__name__).parent / "static/sqr.png").absolute()))

    # service = PlatformLeadsService()
    #
    # parser = PlatformLoginParser(driver=driver)
    #
    # await parser.login(ref_link="https://m.stoloto.ru")


def repl_task():
    asyncio.run(main())


if __name__ == "__main__":
    repl_task()

    # asyncio.run(main())

    # from bot.main import startup
    #
    # startup()

# 2435abb7-53d6-45d0-bf07-a9e1308fb6ae

# https://www.stoloto.ru/private/wallet/refill >
# body > sl-root > ng-component > main > div > ng-component > ng-component > uw-tabview > uw-tabpane:nth-child(2) > div > div > form > uw-form-group > uw-input > label > div.uw-input__body > input
# body > sl-root > ng-component > main > div > ng-component > ng-component > uw-tabview > uw-tabpane:nth-child(2) > div > div > agent-constructor > form > div > div > uw-input > label > div.uw-input__body > input
# body > sl-root > ng-component > main > div > ng-component > ng-component > uw-tabview > uw-tabpane:nth-child(2) > div > div > uw-form-group > uw-button > button
# TAG ngx-qrcode-styling
