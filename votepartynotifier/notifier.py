import argparse
import signal
import sys
import time

from bs4 import BeautifulSoup
import requests

PARTY_FREQ = 100  # Number of votes between each vote party
ENDPOINT = "http://blissscape.net/vote/templates/stats_index.php"


def sigint_handler(signalnum, frame):
    sys.exit(0)


def parse(html) -> int:
    soup = BeautifulSoup(html, "html.parser")
    result = soup.find("h3")

    if not result:
        raise RuntimeError("Failed to parse the HTML response.")

    try:
        votes = result.string.replace(",", "")
        return int(votes)
    except ValueError:
        raise ValueError("Could not convert the votes to an integer.")


def poll(rate: float):
    with requests.Session() as session:
        while True:
            response = session.get(ENDPOINT)
            response.raise_for_status()

            yield response.text

            time.sleep(rate)


def notify(rate: float, current_votes: int):
    prev = None
    for response in poll(rate):
        votes = parse(response)

        if prev is None:
            prev = votes
            continue

        diff = prev - votes
        current_votes += diff

        if current_votes > 0 and current_votes % PARTY_FREQ == 0:
            print("Vote party now!")
            sys.stdout.flush()


def main():
    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser("BlissScape vote party notifier")
    parser.add_argument(
        "--rate",
        "-r",
        type=float,
        default=5,
        help="The rate, in seconds, at which to poll the API."
    )
    parser.add_argument(
        "--votes",
        "-v",
        type=int,
        help="The current amount of votes."
    )
    args = parser.parse_args()

    notify(args.rate, args.votes)
