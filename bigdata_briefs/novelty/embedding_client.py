import traceback

import openai

from bigdata_briefs import logger
from bigdata_briefs.metrics import EmbeddingsMetrics
from bigdata_briefs.models import EmbeddingsUsage
from bigdata_briefs.settings import settings
from bigdata_briefs.utils import sleep_with_backoff


class EmbeddingClient:
    def __init__(self, model: str, client: openai.OpenAI | None = None):
        self.model = model
        if client is None:
            client = openai.OpenAI()
        self.client = client

    def compute(self, texts: list[str], **kwargs) -> list[list[float]]:
        try:
            response = self._embeddings_with_retries(
                func=self.client.embeddings.create,
                input=texts,
                model=self.model,
                encoding_format="float",
            )

            embeddings = [embedding.embedding for embedding in response.data]
            token_count = response.usage.prompt_tokens

        except Exception:
            logger.error(
                f"Error computing embeddings {self.model=}, {texts=}, {kwargs=} {traceback.format_exc()}"
            )
            raise

        EmbeddingsMetrics.track_usage(
            EmbeddingsUsage(model=self.model, tokens=token_count)
        )

        return embeddings

    def _embeddings_with_retries(self, func, *args, **kwargs):
        for attempt in range(settings.EMBEDDING_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception:
                if attempt >= settings.EMBEDDING_RETRIES - 1:
                    raise
                sleep_with_backoff(attempt=attempt)
