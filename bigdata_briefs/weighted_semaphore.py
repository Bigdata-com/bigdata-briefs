import threading
from contextlib import contextmanager


class WeightedSemaphore:
    def __init__(self, weight_available: int):
        self._condition = threading.Condition()
        self._weight_available = weight_available

    @contextmanager
    def __call__(self, weight: int):
        with self._condition:
            while self._weight_available < weight:
                self._condition.wait()
            self._weight_available -= weight
        try:
            yield
        finally:
            with self._condition:
                self._weight_available += weight
                self._condition.notify_all()

    def weight_available(self) -> int:
        with self._condition:
            return self._weight_available