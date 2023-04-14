from classes.Events import Events
import os
import pickle


def load_events() -> Events:
    if os.path.isfile("objects/Events.obj"):
        # Create reference to stored Event object
        f = open("objects/Events.obj", "rb")
        # Store in value e
        e: Events = pickle.load(f)
        # Close file
        f.close()
        return e
    return Events([])


def save_events(e: Events) -> None:
    # Create reference to stored Event object
    f = open("objects/Events.obj", "wb")

    # Serialize event and save to environment variable
    pickle.dump(e, f)

    # Close
    f.close()
