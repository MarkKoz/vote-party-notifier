import signal
import sys
import time

import requests

POLL_RATE = 5
ENDPOINT = "http://blissscape.net/vote/templates/stats_index.php"


def sigint_handler(signalnum, frame):
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, sigint_handler)

    with requests.Session() as session:
        while True:
            response = session.get(ENDPOINT)
            response.raise_for_status()

            print(response.text)
            sys.stdout.flush()

            time.sleep(POLL_RATE)
