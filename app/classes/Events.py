from classes.Event import Event, Status


class Events:
    def __init__(self, events: list[Event]):
        self.events = events

    def add_event(self, e: Event) -> None:
        match e.event_status():
            case Status.READY | Status.STARTED:
                self.events.append(e)

    def filter_event(self, event_id: str) -> Event:
        e: list[Event] = list(filter(lambda event: event.id.lower() == event_id.lower(), self.events))
        match e:
            case e if len(e) > 0:
                return e[0]

    def print_events(self) -> str:
        match len(self.events):
            case 0:
                return "There are currently no active events."
            case _:
                return "The following events are active:\n" + "\n".join(
                    [event.id for event in self.events if event.event_status() != Status.FINISHED]
                )

    def update_event(self, event_id: str, new_event: Event) -> None:
        e: Event = self.filter_event(event_id)
        match e:
            case Event():
                position: int = self.events.index(e)
                self.events.pop(position)
                self.events.insert(position, new_event)
