import json

import openai
from pydantic import BaseModel

from bigdata_briefs import LOG_LEVEL, logger
from bigdata_briefs.metrics import LLMMetrics
from bigdata_briefs.models import LLMUsage
from bigdata_briefs.settings import settings
from bigdata_briefs.utils import (
    log_args,
    log_return_value,
    log_time,
    sleep_with_backoff,
)


class FollowUpQuestionsPromptDefaults(BaseModel):
    n_followup_queries: int = settings.LLM_FOLLOW_UP_QUESTIONS


class LLMClient:
    def __init__(self, client: openai.OpenAI | None = None):
        if client is None:
            client = openai.OpenAI(
                timeout=settings.OPENAI_TIMEOUT_SECONDS,
                max_retries=settings.LLM_RETRIES,
            )
        self.client = client

    @log_time
    @log_args
    @log_return_value
    def call_with_response_format(
        self, *args, system: list, messages: list, model: str, max_tokens: int, **kwargs
    ):
        messages = system + messages
        logger.debug(
            f"Calling {model} with messages: \n {json.dumps(messages, indent=2)}"
        )
        response = self._call_with_retries(
            self.client.responses.parse,
            *args,
            input=messages,
            model=model,
            max_output_tokens=max_tokens,
            **kwargs,
        )

        LLMMetrics.track_usage(
            LLMUsage(
                model=model,
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.total_tokens,
            )
        )

        content = response.output_parsed

        return content

    @log_time
    @log_args
    @log_return_value
    def call_without_response_format(
        self, *args, messages: list, model: str, max_tokens: int, **kwargs
    ):
        logger.debug(
            f"Calling {model} with messages: \n {json.dumps(messages, indent=2)}"
        )
        response = self._call_with_retries(
            self.client.chat.completions.create,
            *args,
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            **kwargs,
        )

        LLMMetrics.track_usage(
            LLMUsage(
                model=model,
                prompt_tokens=response["usage"]["inputTokens"],
                completion_tokens=response["usage"]["outputTokens"],
                total_tokens=response["usage"]["totalTokens"],
            )
        )

        return response["output"]["message"]["content"][0]["text"]

    def _call_with_retries(self, func, *args, **kwargs):
        for attempt in range(settings.LLM_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if LOG_LEVEL == "DEBUG" and "timeout" in str(e).lower():
                    prompt_payload = kwargs.get("input") or kwargs.get("messages")
                    print(
                        "\n[DEBUG][LLM TIMEOUT] Prompt payload sent to LLM:\n",
                        json.dumps(prompt_payload, indent=2, ensure_ascii=False),
                    )
                if attempt >= settings.LLM_RETRIES - 1:
                    raise
                logger.warning(f"Error calling LLM: {e}. Attempt {attempt + 1}")
                sleep_with_backoff(attempt=attempt)
