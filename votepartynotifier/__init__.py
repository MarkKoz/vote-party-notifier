import logging
import sys

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(stream=sys.stdout)]
)
