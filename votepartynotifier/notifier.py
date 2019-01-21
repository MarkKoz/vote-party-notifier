import signal
import sys


def sigint_handler(signalnum, frame):
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, sigint_handler)

