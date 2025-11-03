import warnings
from collections import deque
from math import floor
from threading import Lock
from time import perf_counter, sleep

from bigdata_briefs import logger
from bigdata_briefs.exceptions import TooManyAPIRetriesError

# Define a high max retries to avoid infinite loops in rate limiter
MAX_RETRIES_RATE_LIMITER = 10000
LOG_WARNING_EVERY_N_RETRIES = 100
RAISE_WARNING_EVERY_N_RETRIES = 1000


class RequestsPerMinuteController:
    def __init__(
        self,
        *,
        max_requests_per_min: int,
        rate_limit_refresh_frequency: float,
        seconds_before_retry: float,
    ):
        """This class will control the rate limit of requests per minute

        Internally, it will actually rate limit per `max_requests_per_min` seconds to avoid
        frontloading the requests and to allow for a more even distribution of requests over the
        full minute.

        :param max_requests_per_min: The maximum number of requests per minute allowed.
        :param rate_limit_refresh_frequency: The frequency at which the rate limit will refresh, lower
            values will allow for requests to be executed with a better spread over the minute.
        :param seconds_before_retry: The time in seconds before retrying the request.
        """
        self.lock = Lock()
        self.rate_limit_refresh_frequency = rate_limit_refresh_frequency
        self.max_requests_per_refresh = floor(
            max_requests_per_min / floor(60 / self.rate_limit_refresh_frequency)
        )
        self.time_before_retry = seconds_before_retry
        self.deque = deque(maxlen=self.max_requests_per_refresh)

    def __call__(self, func, *args, **kwargs):
        """This will attempt to execute any function while taking into account the rate limit"""
        # Effectively a while(True), but safer
        for idx in range(MAX_RETRIES_RATE_LIMITER):
            if self._allowed_by_rate_limit():
                return func(*args, **kwargs)
            if idx > 0 and idx % LOG_WARNING_EVERY_N_RETRIES == 0:
                logger.warning("Handling requests throttle.", retries_attempted=idx)
            if idx > 0 and idx % RAISE_WARNING_EVERY_N_RETRIES == 0:
                warnings.warn(
                    f"Handling requests throttle. Retries attempted: {idx}",
                    RuntimeWarning,
                    stacklevel=3,
                )
            sleep(self.time_before_retry)

        raise TooManyAPIRetriesError(
            f"Exceeded max retries on rate limiter. {MAX_RETRIES_RATE_LIMITER} retries exceeded over a period of {MAX_RETRIES_RATE_LIMITER * self.time_before_retry} seconds for a single request"
        )

    def _allowed_by_rate_limit(self) -> bool:
        # If the deque is not full or the oldest request is older than the refresh frequency
        # allow a new request through
        with self.lock:
            if (
                len(self.deque) < self.max_requests_per_refresh
                or perf_counter() - self.deque[0] > self.rate_limit_refresh_frequency
            ):
                self.deque.append(perf_counter())
                return True

            return False
