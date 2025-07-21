import logging
from importlib.metadata import version

import structlog

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)


__version__ = version("bigdata_briefs")
logger = structlog.get_logger().bind(logger="briefs-service")
