import concurrent.futures
import time
import warnings

import pytest

from bigdata_briefs.query_service import rate_limit
from bigdata_briefs.exceptions import TooManyAPIRetriesError


def test_rpmc_allows_request():
    rpmc = rate_limit.RequestsPerMinuteController(
        max_requests_per_min=200,
        seconds_before_retry=1,
        rate_limit_refresh_frequency=10,
    )

    result = rpmc(lambda: True)

    assert result is True, "The request result was not as expected"


def test_rpmc_blocks_on_limit():
    # Configure the request controller with tiny limits to test the blocking
    # of a request without making the unit test too slow.
    rpmc = rate_limit.RequestsPerMinuteController(
        max_requests_per_min=300,  # Ensure the quota is filled with only one request per refresh
        seconds_before_retry=0.1,  # Retry the request fast to not block
        rate_limit_refresh_frequency=0.2,  # Check the rate limit every 0.2 seconds
    )

    # This call should fill the quota
    result = rpmc(lambda: True)
    assert result is True, "The request results was not as expected"

    # This call should be blocked
    with pytest.raises(concurrent.futures.TimeoutError):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(rpmc, lambda: True)
            result = future.result(
                timeout=0.1
            )  # The timeout should be less than the refresh frequency


def test_rpmc_allows_after_limit_refresh():
    # Configure the request controller with tiny limits to test the blocking
    # of a request without making the unit test too slow.
    refresh_period = 0.2
    rpmc = rate_limit.RequestsPerMinuteController(
        max_requests_per_min=300,  # Ensure the quota is filled with only one request per refresh
        seconds_before_retry=0.1,  # Retry the request fast to not block
        rate_limit_refresh_frequency=refresh_period,  # Check the rate limit every 0.2 seconds
    )
    start_time = time.time()
    # This call should fill the quota
    result = rpmc(lambda: True)
    assert result is True, "The first request results was not as expected"

    # This call should be blocked until next refresh, then allowed
    second_result = rpmc(lambda: True)
    assert second_result is True, "The second request result was not as expected"
    assert (
        time.time() - start_time > refresh_period
    ), "The second request was executed faster than expected"


def test_rpmc_safely_avoids_infinite_loops():
    # Configure the request controller so that it retries very fast and consumes the limit to
    # avoid infinite loops.
    rpmc = rate_limit.RequestsPerMinuteController(
        max_requests_per_min=1,  # Ensure the quota is filled with only one request per refresh
        seconds_before_retry=0,  # Set to 0 to retry as fast as possible
        rate_limit_refresh_frequency=60,  # Rate limit may be slow in this test
    )

    # Fill the quota
    rpmc(lambda: True)

    # As seconds before retry is 0, this should very quickly exceed the max retries and
    # raise the exception
    with pytest.raises(
        TooManyAPIRetriesError, match="Exceeded max retries on rate limiter."
    ):
        # This code raises a lot of warnigs as we are retrying very fast, ignore them during this unit test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rpmc(lambda: True)
