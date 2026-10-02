import logging
import sys


def configure_logging(env: str = "development") -> None:
    level = logging.INFO if env == "production" else logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Quiet down noisy third-party loggers so prediction/auth logs stand out.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
