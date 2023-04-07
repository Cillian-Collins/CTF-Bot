from classes.Event import Event
import os
import pickle


def load_event() -> Event:
    if os.path.isfile("objects/Event.obj"):
        # Create reference to stored Event object
        f = open("objects/Event.obj", "rb")
        # Store in value e
        e: Event = pickle.load(f)
        # Close file
        f.close()
        return e
    return None


def save_event(e: Event) -> None:
    # Create reference to stored Event object
    f = open("objects/Event.obj", "wb")

    # Serialize event and save to environment variable
    pickle.dump(e, f)

    # Close
    f.close()
