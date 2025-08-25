import logging
import sys
from pythonjsonlogger.json import JsonFormatter


def setup_logging():
    """
    Configures structured (JSON) logging for the application.
    """
    log = logging.getLogger()
    if log.handlers:
        for handler in log.handlers:
            log.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)

    formatter = JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)

    log.addHandler(handler)
    log.setLevel(logging.INFO)

    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
