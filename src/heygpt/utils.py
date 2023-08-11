import logging
import os
from rich.logging import RichHandler
from dotenv import load_dotenv

load_dotenv()


def _logger(flag: str = "", format: str = ""):
    if format == "" or format == None:
        format = "%(levelname)s|%(name)s| %(message)s"

    # message
    logger = logging.getLogger(__name__)

    if os.environ.get(flag) != None:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # create console handler and set level to debug
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # # create formatter
    # # add formatter to ch
    # formatter = logging.Formatter(format)
    # ch.setFormatter(formatter)

    # # add ch to logger
    # logger.addHandler(ch)
    handler = RichHandler(log_time_format="")
    logger.addHandler(handler)
    return logger


# message
# export LOG_LEVEL=DEBUG
log = _logger("LOG_LEVEL")


def notNone(data, type):
    if isinstance(data, str) and len(data.strip()) == 0:
        return False
    elif isinstance(data, type) and len(data) != 0:
        return True
    else:
        return False
