
import pytest
from pydantic import BaseModel, ValidationError

from bigdata_briefs.utils import (
    log_args,
    log_performance,
    log_return_value,
    log_time,
    sleep_with_backoff,
    validate_and_repair_model,
)
from bigdata_briefs.utils import time as utils_time  # For monkeypatching in tests


class DummyModel(BaseModel):
    x: int


@pytest.mark.parametrize(
    "decorator", [log_time, log_args, log_return_value, log_performance]
)
def test_decorator_does_not_affect_output(decorator):
    @decorator
    def foo():
        return "bar"

    result = foo()
    assert result == "bar"


def test_validate_and_repair_model_valid():
    json_str = '{"x": 5}'
    result = validate_and_repair_model(json_str, DummyModel)
    assert isinstance(result, DummyModel)
    assert result.x == 5


def test_validate_and_repair_model_various_inputs():
    json_str = "{x:5}"  # missing quotes around key
    result = validate_and_repair_model(json_str, DummyModel)
    assert isinstance(result, DummyModel)
    assert result.x == 5


def test_validate_and_repair_model_fails():
    broken_json = "{}"
    with pytest.raises(ValidationError):
        validate_and_repair_model(broken_json, DummyModel)


def test_sleep_with_backoff_sleeps(monkeypatch):
    sleep_calls = []
    monkeypatch.setattr(utils_time, "sleep", lambda t: sleep_calls.append(t))
    for i in range(5):
        sleep_with_backoff(base=1, attempt=i)

    assert len(sleep_calls) == 5
    min_sleep = 0.5
    for attempt, sleep_time in enumerate(sleep_calls):
        max_sleep = 1 * 2**attempt  # Base times 2 to the power of attempt
        assert min_sleep <= sleep_time <= max_sleep, (
            f"Sleep time {sleep_time} out of bounds for attempt {attempt}"
        )
