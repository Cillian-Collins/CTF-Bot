from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from enum import Enum


class Event:
    def __init__(
        self,
        event_id: str,
        name: str,
        description: str,
        start: str,
        finish: str,
        url: str,
    ):
        self.id = event_id
        self.name = name
        self.description = description
        self.start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
        self.finish = datetime.strptime(finish, "%Y-%m-%dT%H:%M:%S%z")
        self.url = url
        self.channel = None
        self.role = None

    def add_player(self, player_id: str) -> None:
        # Assign the player a role
        return

    def event_status(self) -> Enum:
        match self:
            case _ if datetime.now(timezone.utc) < self.start:
                # Event has not started yet
                return Status.READY
            case _ if datetime.now(timezone.utc) < self.finish:
                # Event is ongoing
                return Status.STARTED
            case _:
                # Event has finished
                return Status.FINISHED

    def status(self) -> str:
        status: Enum = self.event_status()
        match status:
            case Status.READY:
                # Event has not started yet
                return self.__time_until_event()
            case Status.STARTED:
                # Event is ongoing
                return self.__time_until_finish()
            case Status.FINISHED:
                # Event has finished
                return "The event has ended."

    def set_role(self, role_id: str) -> None:
        self.role = role_id

    def set_name(self, name: str) -> None:
        self.name = name

    def set_description(self, description: str) -> None:
        self.description = description

    def set_url(self, url: str) -> None:
        self.url = url

    def set_start(self, start: str) -> None:
        self.start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")

    def set_finish(self, finish: str) -> None:
        self.finish = datetime.strptime(finish, "%Y-%m-%dT%H:%M:%S%z")

    def set_channel(self, channel: int) -> None:
        self.channel = channel

    def running_time(self) -> str:
        td = relativedelta(self.finish, self.start)
        return f"The CTF will run for {self.__relative_delta_to_string(td)}."

    def __time_until_event(self) -> str:
        return self.__date_time_parse_message(self.start, "begins")

    def __time_until_finish(self) -> str:
        return self.__date_time_parse_message(self.finish, "ends")

    def __date_time_parse_message(self, dt: datetime, m: str) -> str:
        ts = round(dt.timestamp())
        output = f"{self.name} {m} <t:{ts}:R>.\nMore information: {self.url}"
        return output

    @staticmethod
    def __relative_delta_to_string(td: relativedelta) -> str:
        output_array = []
        if td.days != 0:
            output_array.append(f"{abs(td.days)} days")
        if td.hours != 0:
            output_array.append(f"{abs(td.hours)} hours")
        if td.minutes != 0:
            output_array.append(f"{abs(td.minutes)} minutes")
        if td.seconds != 0:
            output_array.append(f"{abs(td.seconds)} seconds")
        output_array = map(lambda x: x[:-1] if x[0] == "1" else x, output_array)
        output = ", ".join(output_array)
        return output


class Status(Enum):
    READY = 0
    STARTED = 1
    FINISHED = 2
