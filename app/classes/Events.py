from classes.Event import Event, Status
from thefuzz import process


class Events:
    def __init__(self, events: list[Event]):
        self.events = events

    def add_event(self, e: Event) -> None:
        match e.event_status():
            case Status.READY | Status.STARTED:
                self.events.append(e)

    def get_channel_event(self, channel: int) -> Event:
        next((event for event in self.events if event.channel == channel), None)

    def filter_event(self, event_id: str) -> Event:
        event_id, score = process.extractOne(
            event_id, [event.id for event in self.events]
        )
        match score > 50:
            case True:
                e: list[Event] = list(
                    filter(
                        lambda event: event.id.lower() == event_id.lower(), self.events
                    )
                )
                match len(e) > 0:
                    case True:
                        return e[0]

    def print_events(self) -> str:
        active_events = [
            event.id for event in self.events if event.event_status() != Status.FINISHED
        ]
        match len(active_events):
            case 0:
                return "There are currently no active events."
            case _:
                return "The following events are active:\n" + "\n".join(active_events)

    def update_event(self, event_id: str, new_event: Event) -> None:
        e: Event = self.filter_event(event_id)
        match e:
            case Event():
                position: int = self.events.index(e)
                self.events.pop(position)
                self.events.insert(position, new_event)
