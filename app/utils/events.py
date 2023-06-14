from classes.Events import Events
import os
import pickle


def load_events() -> Events:
    if os.path.isfile("objects/Events.obj"):
        # Create reference to stored Event object
        with open("objects/Events.obj", "rb") as f:
            # Store in value e
            e: Events = pickle.load(f)
        return e
    return Events([])


def save_events(e: Events) -> None:
    # Create reference to stored Event object
    with open("objects/Events.obj", "wb") as f:
        # Serialize event and save to environment variable
        pickle.dump(e, f)
