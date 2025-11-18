import os
from typing import Literal

import yaml
from jinja2 import StrictUndefined, Template

from bigdata_briefs.models import PromptConfig

base_dir = os.path.dirname(os.path.abspath(__file__))
PROMPT_FILE = os.path.join(base_dir, "prompts.yaml")


def get_prompt_keys(
    prompt_name: Literal[
        "entity_update",
        "follow_up_questions",
        "intro_section",
        "report_title",
    ],
) -> PromptConfig:
    with open(PROMPT_FILE, "r") as f:
        properties = yaml.safe_load(f)[prompt_name]
        system_prompt = properties.pop("system_prompt")
        user_template = properties.pop("user_template")

        return PromptConfig(
            system_prompt=system_prompt,
            user_template=Template(user_template, undefined=StrictUndefined),
            llm_kwargs={**properties["model_kwargs"], "model": properties["model"]},
        )
