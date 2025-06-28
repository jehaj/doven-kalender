import sys

from kalender import get_events, JSONType


def get_event_description(event: JSONType):
    pass


def generate_description(event: dict[str, str]):
    pass


def weekday_name(weekday_index: int):
    names = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
    return names[weekday_index]


if __name__ == "__main__":
    print("Doven Kalender")
    events = get_events("fj88e45fvuj2hfhl3n1g0mlkus")
    if not len(events):
        print("Der er ingen begivenheder i den kommende uge.")
        sys.exit(0)
    event = None
    get_event_description(event)
    post_description = generate_description(None)
