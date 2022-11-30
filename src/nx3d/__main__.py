import os
import sys

from loguru import logger

import nx3d

if __name__ == "__main__":

    logger.remove()
    if os.environ.get("TRACE"):
        logger.add(sys.stderr, level="TRACE")
    elif os.environ.get("DEBUG"):
        logger.add(sys.stderr, level="DEBUG")
    elif os.environ.get("INFO"):
        logger.add(sys.stderr, level="INFO")
    else:
        logger.add(sys.stderr, level="WARNING")

    if len(sys.argv) > 1:
        nx3d.demo(**{arg: True for arg in sys.argv[1:]})
    else:
        nx3d.demo()
