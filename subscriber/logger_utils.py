import os
import logging


def get_logger(name=__name__, log_file="publisher.log", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Stop logs from propagating to root (prevents console output)
    logger.propagate = False

    # Only add a file handler if log_file is provided
    if log_file:
        fh = logging.FileHandler(log_file, mode="a")  # overwrite each run
        fh.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(fh)

    return logger


def clear_log(log_file="publisher.log"):
    """Overwrite the log file with an empty file to start fresh."""
    if os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("")  # clear the contents
