import random
import time
import traceback
import warnings
from datetime import datetime
from functools import wraps
from time import perf_counter
from typing import Type

from json_repair import repair_json
from pydantic import BaseModel, ValidationError

from bigdata_briefs import logger


def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            logger.debug(f"{func.__name__} executed in {perf_counter() - start}s")

    return wrapper


def log_args(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"{func.__name__} executed with {args=} and {kwargs=}")
        return func(*args, **kwargs)

    return wrapper


def log_return_value(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        logger.debug(f"{func.__name__} returned {value=}")
        return value

    return wrapper


def log_performance(func):
    @wraps(func)
    def wrapper(
        *args, enable_metric: bool = False, metric_name: str = "Undefined", **kwargs
    ):
        start = perf_counter()
        value = func(*args, **kwargs)
        if enable_metric:
            timing = datetime.now()
            msg = f"{timing.strftime('%I:%M:%S')}.{timing.microsecond // 10000:02d} - {metric_name} - {round(time.perf_counter() - start, 2)}"
            logger.debug(msg)
        return value

    return wrapper


def validate_and_repair_model(json_str: str, model: Type[BaseModel]) -> BaseModel:
    try:
        response = model.model_validate_json(json_str)
        return response
    except ValidationError:
        # With return_objects=False, it always returns a string, so ignore type checking error
        fixed_json_str: str = repair_json(json_str, return_objects=False)  # type: ignore[invalid-assignment]
        try:
            response = model.model_validate_json(fixed_json_str)
            logger.debug(
                f"The following could not be parsed as a {model.__name__}, but we could repair the json\n{json_str=}\n{fixed_json_str=}"
            )
            return response
        except ValidationError:
            logger.warning(
                f"The following LLM completion could not be parsed as a {model.__name__}, nor could it be repaired\n{json_str=}\n{fixed_json_str=}"
            )
            raise


def sleep_with_backoff(*, base: int = 1, attempt: int):
    """
    Sleeps for an amount of time. This amount is calculated
    with backoff and jitter taking into account the number
    of retries.

    @attempt starts at 0

    """
    max_sleep = 20

    rnd_upper_bound = min(max_sleep, base * 2**attempt)
    sleep_time = round(random.uniform(0.5, rnd_upper_bound), 2)

    logger.debug(f"Sleeping for {sleep_time}")

    time.sleep(sleep_time)


def raise_warning_from(e, category=RuntimeWarning):
    """Issue a warning derived from an exception object."""
    tb_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    warnings.warn(
        f"Converted exception to warning:\n{tb_str.strip()}", category, stacklevel=2
    )
