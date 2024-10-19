from .base import BaseService
from dataclasses import dataclass


@dataclass
class Session:
    count_requests: int
    ref_link: str
    phone_number: str
    count_successed: int = "x"

    @classmethod
    def from_dict(cls, dict_: dict):
        return Session(
            **{i: dict_[i]
               for i in dict_.keys()
               if i in cls.__annotations__.keys()}
        )


class SessionsService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.get_count():
            self._init_sessions_counter()

    def get_all(self) -> list[str]:
        data = self._conn.mget([
            f"sessions:session#{i}" for i in range(1, self.get_count()+1)
        ])

        return data

    def get_count(self) -> int:
        try:
            return int(self._conn.get("sessions:count"))
        except:
            return None

    def increase_count(self):
        pipe = self._conn.pipeline()

        current = self.get_count()
        current += 1

        pipe.set(name="sessions:count", value=current)
        pipe.execute()

    def add(self, passed_session: Session):
        count = self.get_count()

        self._conn.append(key=f"sessions:session#{count+1}",
                          value=f"{passed_session.count_requests}@"
                                f"{passed_session.count_successed}@"
                                f"{passed_session.ref_link}@"
                                f"{passed_session.phone_number}"
                          )

        self.increase_count()

    def _init_sessions_counter(self):
        self._conn.append("sessions:count", 0)
