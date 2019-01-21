import argparse
import signal
import sys
import time

from bs4 import BeautifulSoup
import requests

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


def poll(rate: float, current_votes: int):
    with requests.Session() as session:
        while True:
            response = session.get(ENDPOINT)
            response.raise_for_status()

            votes = parse(response.text)
            print(votes)
            sys.stdout.flush()

            time.sleep(rate)


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

    poll(args.rate, args.votes)
