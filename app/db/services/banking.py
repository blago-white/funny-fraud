import time

from .base import BaseService


class BotBankingStatusService(BaseService):
    def authenticated(self, phone: str):
        self._conn.append(
            "bank:status", f"{phone}:{time.time()}"
        )

    def unauthenticated(self):
        self._conn.set("bank:status", "")

    def status(self):
        status = self._conn.get("bank:status")

        if not status:
            return False, "🚫Банкинг не привязан"

        phone = str(status).split(":")[0]

        return True, f"🌐Актуальный банкинг: <code>{phone[2:-1]}</code>"

    def get_number(self):
        status = self._conn.get("bank:status")

        if not status:
            return "xxx"

        return str(status).split(":")[0]
