from abc import ABC, abstractmethod
from queue import Queue
from threading import Lock

from bigdata_briefs.models import (
    BulletPointsUsage,
    EmbeddingsUsage,
    LLMUsage,
    TopicContentTracker,
)


class Metrics(ABC):
    @classmethod
    @abstractmethod
    def track_usage(cls, usage): ...

    @classmethod
    @abstractmethod
    def get_total_usage(cls): ...

    @classmethod
    def reset_usage(cls):
        with cls.lock:
            cls.metrics_queue.queue.clear()


class CacheMetrics(Metrics):
    metrics_queue = Queue()
    lock = Lock()

    @classmethod
    def track_usage(cls, usage: int = 1):
        cls.metrics_queue.put(usage)

    @classmethod
    def get_total_usage(cls) -> int:
        with cls.lock:
            usages = cls.metrics_queue.queue
            if not usages:
                return 0
            return sum(usages)


class QueryUnitMetrics(Metrics):
    metrics_queue = Queue()
    lock = Lock()

    @classmethod
    def track_usage(cls, usage: int):
        cls.metrics_queue.put(usage)

    @classmethod
    def get_total_usage(cls) -> int:
        with cls.lock:
            usages = cls.metrics_queue.queue
            if not usages:
                return 0
            return sum(usages)


class BulletPointMetrics(Metrics):
    metrics_queue = Queue()
    lock = Lock()

    @classmethod
    def track_usage(cls, usage: BulletPointsUsage):
        cls.metrics_queue.put(usage)

    @classmethod
    def get_total_usage(cls):
        with cls.lock:
            usages = cls.metrics_queue.queue
            if not usages:
                return BulletPointsUsage()

            return sum(cls.metrics_queue.queue, start=BulletPointsUsage())


class LLMMetrics:
    """
    This class does not inherit from Metrics, this is a more complex class and it doesn't work with
    a queue. It tracks usage per model and aggregates it using a dict.
    """

    usage_per_model: dict[str, LLMUsage] = {}
    lock = Lock()

    @classmethod
    def track_usage(cls, usage: LLMUsage):
        """Track LLM usage, aggregating by model."""
        if usage.is_empty():
            return

        with cls.lock:
            if usage.model not in cls.usage_per_model:
                # First usage for this model
                cls.usage_per_model[usage.model] = usage
            else:
                # Add to existing usage for this model
                cls.usage_per_model[usage.model] += usage

    @classmethod
    def get_total_usage(cls) -> LLMUsage:
        """Get total usage across all models. For backward compatibility."""
        summary = cls.get_usage_summary()
        if not summary:
            return LLMUsage()

        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_n_calls = 0
        total_tokens = 0

        for usage in summary.values():
            total_prompt_tokens += usage.prompt_tokens
            total_completion_tokens += usage.completion_tokens
            total_tokens += usage.total_tokens
            total_n_calls += usage.n_calls

        return LLMUsage(
            model="multiple",
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_completion_tokens,
            total_tokens=total_tokens,
            n_calls=total_n_calls,
        )

    @classmethod
    def get_usage_summary(cls) -> dict[str, LLMUsage]:
        """Get usage breakdown by model"""
        with cls.lock:
            if not cls.usage_per_model:
                return {}

            # Create a deep copy to avoid modifying tracking data
            summary = {
                model: usage.model_copy(deep=True)
                for model, usage in cls.usage_per_model.items()
            }

            return summary

    @classmethod
    def reset_usage(cls):
        with cls.lock:
            cls.usage_per_model.clear()


class EmbeddingsMetrics(Metrics):
    metrics_queue = Queue()
    lock = Lock()

    @classmethod
    def track_usage(cls, usage: EmbeddingsUsage):
        cls.metrics_queue.put(usage)

    @classmethod
    def get_total_usage(cls) -> EmbeddingsUsage:
        with cls.lock:
            usages = cls.metrics_queue.queue
            if not usages:
                return EmbeddingsUsage()
            model = usages[0].model

            total_usage = sum(
                cls.metrics_queue.queue, start=EmbeddingsUsage(model=model)
            )

            return total_usage


class ContentMetrics(Metrics):
    metrics_queue = Queue()
    lock = Lock()

    @classmethod
    def track_usage(cls, usage: TopicContentTracker):
        cls.metrics_queue.put(usage)

    @classmethod
    def get_total_usage(cls) -> dict[str, TopicContentTracker]:
        with cls.lock:
            usages = cls.metrics_queue.queue
            if not usages:
                return {}
            return TopicContentTracker.aggregate_per_topic(usages)
