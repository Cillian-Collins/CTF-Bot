from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import discord
import os
import pickle


class Event:
    def __init__(self, name: str, description: str, start: str, finish: str, url: str):
        self.name = name
        self.description = description
        self.start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
        self.finish = datetime.strptime(finish, "%Y-%m-%dT%H:%M:%S%z")
        self.url = url

    def add_player(self, player_id: str) -> None:
        # Assign the player a role
        return

    def status(self) -> str:
        match self:
            case _ if datetime.now(timezone.utc) < self.start:
                # Event has not started yet
                return self.__time_until_event()
            case _ if datetime.now(timezone.utc) < self.finish:
                # Event is ongoing
                return self.__time_until_finish()
            case _:
                # Event has finished
                return "The event has ended."

    def __time_until_event(self) -> str:
        td = relativedelta(self.start, datetime.now(timezone.utc))
        return self.__relative_delta_to_string(td, "begins")

    def __time_until_finish(self) -> str:
        td = relativedelta(datetime.now(timezone.utc), self.finish)
        return self.__relative_delta_to_string(td, "ends")

    def __relative_delta_to_string(self, td, m) -> str:
        output_array = []
        output_array.append(f"{td.days} days") if td.days > 0 else None
        output_array.append(f"{td.hours} hours") if td.hours > 0 else None
        output_array.append(f"{td.minutes} minutes") if td.minutes > 0 else None
        output_array.append(f"{td.seconds} seconds") if td.seconds > 0 else None
        output = ", ".join(output_array)
        output += f" until {self.name} {m}.\nMore information: {self.url}"
        return output

