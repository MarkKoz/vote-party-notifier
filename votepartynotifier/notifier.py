import argparse
import logging
import signal
import sys
import time
from pathlib import Path

import arrow
import ntfy
import requests
from bs4 import BeautifulSoup
from ntfy import data as ntfy_data

PARTY_FREQ = 100  # Number of votes between each vote party
ENDPOINT = "http://blissscape.net/vote/templates/stats_index.php"
SERVER_TZ = "America/New_York"

log = logging.getLogger(__name__)


def sigint_handler(signalnum, frame):
    log.warning("Received SIGINT; exiting...")
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


def _request(rate: float, session: requests.Session) -> requests.Response:
    while True:
        try:
            return session.get(ENDPOINT)
        except requests.exceptions.ConnectionError:
            log.exception(
                f"Error connecting to the vote stats endpoint. "
                "Trying again in {rate} seconds."
            )
            time.sleep(rate)


def request(rate: float, session: requests.Session) -> requests.Response:
    response = _request(rate, session)
    while response.status_code != 200:
        log.error(
            f"Response status was {response.status_code}. "
            f"Trying again in {rate} seconds."
        )
        time.sleep(rate)
        response = _request(rate, session)

    return response


def poll(rate: float) -> str:
    with requests.Session() as session:
        while True:
            response = request(rate, session)
            yield response.text
            time.sleep(rate)


def notify(rate: float, current_votes: int, threshold: int):
    prev_votes = None
    prev_time = None
    notified = False

    for response in poll(rate):
        votes = parse(response)
        time = arrow.now(SERVER_TZ)

        if prev_votes is None:
            prev_votes = votes
            prev_time = time

            log.info(f"Votes: {votes} ({current_votes})")
            continue

        if time.day != prev_time.day:
            current_votes = 0
            notified = False

        if time.month != prev_time.month:
            prev_votes = votes

        current_votes += votes - prev_votes
        prev_votes = votes
        prev_time = time

        if current_votes > 0:
            remainder = (current_votes + threshold) % PARTY_FREQ
            if not notified and 0 <= remainder < threshold:
                notified = True
                message = f"Vote party in less than {threshold} votes!"

                log.info(message)
                ntfy.notify(message, "BlissScape Vote Party")
            elif remainder >= threshold:
                if notified:
                    log.info("New vote party interval")
                notified = False

        log.info(f"Votes: {votes} ({current_votes})")


def validate_threshold(threshold: str):
    threshold = int(threshold)
    if threshold >= PARTY_FREQ:
        raise argparse.ArgumentTypeError(
            f"{threshold} is not less than the vote party frequency"
            "({PARTY_FREQ})"
        )

    return threshold


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
        required=True,
        help="The current amount of votes."
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=validate_threshold,
        default=10,
        help="The amount of votes that must remain before notifying."
    )
    args = parser.parse_args()

    try:
        ntfy_data.icon.png = str(Path("res/BlissScape.png").resolve(True))
        ntfy_data.icon.ico = str(Path("res/BlissScape.ico").resolve(True))
    except FileNotFoundError:
        log.exception(
            "Could not find icon files; falling back to ntfy's defaults. "
            "Is the current working directory not the root of the repository?"
        )

    notify(args.rate, args.votes, args.threshold)
