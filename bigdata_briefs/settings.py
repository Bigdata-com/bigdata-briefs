from pathlib import Path
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings

from bigdata_briefs import logger

DEFAULT_TOPICS = [
    "What key takeaways emerged from {company}'s latest earnings report?",
    "What notable changes in {company}'s financial performance metrics have been reported recently?",
    "Has {company} revised its financial or operational guidance for upcoming periods?",
    "What significant strategic initiatives or business pivots has {company} announced recently?",
    "What material acquisition, merger, or divestiture activities involve {company} currently?",
    "What executive leadership changes have been announced at {company} recently?",
    "What significant contract wins, losses, or renewals has {company} recently announced?",
    "What significant new product launches or pipeline developments has {company} announced?",
    "What material operational disruptions or capacity changes is {company} experiencing currently?",
    "How are supply chain conditions affecting {company}'s operations and outlook?",
    "What production milestones or efficiency improvements has {company} achieved recently?",
    "What cost-cutting measures or expense management initiatives has {company} recently disclosed?",
    "What notable market share shifts has {company} experienced recently?",
    "How is {company} responding to new competitive threats or significant competitor actions?",
    "What significant new product launches or pipeline developments has {company} announced?",
    "What specific regulatory developments are materially affecting {company}?",
    "How are current macroeconomic factors affecting {company}'s performance and outlook?",
    "What material litigation developments involve {company} currently?",
    "What industry-specific trends or disruptions are directly affecting {company}?",
    "What significant capital allocation decisions has {company} announced recently?",
    "What changes to dividends, buybacks, or other shareholder return programs has {company} announced?",
    "What debt issuance, refinancing, or covenant changes has {company} recently announced?",
    "Have there been any credit rating actions or outlook changes for {company} recently?",
    "What shifts in the prevailing narrative around {company} are emerging among influential investors?",
    "What significant events could impact {company}'s performance in the near term?",
    "What unexpected disclosures or unusual trading patterns has {company} experienced recently?",
    "Is there any activist investor involvement or significant shareholder actions affecting {company}?",
]


PROJECT_DIRECTORY = Path(__file__).parent.parent

UNSET: Literal["<UNSET>"] = "<UNSET>"


class Settings(BaseSettings):
    # Demo mode - disables "Run Analysis" functionality, only allows pre-computed demos
    # Only affects the frontend, to protect the backend, set ACCESS_TOKEN
    DEMO_MODE: bool = False

    # Required, except on demo mode
    BIGDATA_API_KEY: str | Literal["<UNSET>"] = UNSET
    OPENAI_API_KEY: str | Literal["<UNSET>"] = UNSET

    # Set access token to enable authentication on the endpoints
    ACCESS_TOKEN: str | None = None

    # Data storage configuration
    DB_STRING: str = "sqlite:///briefs.db"
    TEMPLATES_DIR: str = str(PROJECT_DIRECTORY / "bigdata_briefs" / "templates")

    # Static dir configuration
    STATIC_DIR: str = str(PROJECT_DIRECTORY / "bigdata_briefs" / "static")

    # General configuration
    WATCHLIST_ITEMS_LIMIT: int = 200
    TOPICS: list[str] = DEFAULT_TOPICS
    INTRO_SECTION_MIN_RELEVANCE_SCORE: int = 3
    MAX_INTRO_SECTION_ENTITIES: int = 8
    DISABLE_INTRO_OVER_N_ENTITIES: int = 100

    # Novelty configuration
    NOVELTY_ENABLED: bool = True
    NOVELTY_MODEL: str = "text-embedding-3-large"
    NOVELTY_THRESHOLD: float = 0.7
    NOVELTY_LOOKBACK_DAYS: int = 14
    NOVELTY_STORAGE_LOOKBACK_HOURS: int = 1
    NOVELTY_STORAGE_THRESHOLD: float = 0.8
    EMBEDDING_RETRIES: int = 3

    # Search configuration
    API_SIMULTANEOUS_REQUESTS: int = 40  # Reduced to prevent rate limit bursts
    API_BASE_URL: str = "https://api.bigdata.com"
    API_CHUNKS_LIMIT_EXPLORATORY: int = 15
    API_RERANK_EXPLORATORY: float = 0.8
    EXPLORATORY_SENTIMENT_THRESHOLD: float = 0.3
    API_CHUNK_LIMIT_FOLLOWUP: int = 15
    API_RERANK_FOLLOWUP: float = 0.9
    FOLLOWUP_SENTIMENT_THRESHOLD: float = 0.3
    API_SOURCE_RANK_BOOST: int = 10
    API_FRESHNESS_BOOST: int = 8
    API_RETRIES: int = 3
    API_TIMEOUT_SECONDS: int = 15

    # LLM configuration
    LLM_FOLLOW_UP_QUESTIONS: int = 5
    LLM_RETRIES: int = 3

    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @classmethod
    def load_from_env(cls) -> "Settings":
        return cls()

    @field_validator("ACCESS_TOKEN", mode="after")
    @classmethod
    def validate_access_token(cls, v: str | None) -> str | None:
        if v is not None and len(v) == 0:
            raise ValueError("ACCESS_TOKEN cannot be an empty string")
        if v is not None and len(v) > 0:
            logger.info(
                "ACCESS_TOKEN is set, the API endpoints will be protected. Use the `token` query parameter to authenticate."
            )
        return v

    @model_validator(mode="after")
    def validate_demo_mode(self) -> "Settings":
        if self.DEMO_MODE:
            logger.warning(
                "DEMO_MODE is enabled. Running new analyses is disabled. "
                "This mode is intended for demonstration purposes only."
            )
        else:
            if self.BIGDATA_API_KEY == UNSET or self.OPENAI_API_KEY == UNSET:
                raise ValueError(
                    "BIGDATA_API_KEY and OPENAI_API_KEY must be set when DEMO_MODE is disabled."
                )
        return self


settings = Settings.load_from_env()
