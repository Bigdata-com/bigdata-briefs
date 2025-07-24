from pathlib import Path

from pydantic_settings import BaseSettings

DEFAULT_TOPICS = {
    # Financial Performance
    "Earnings": "What key takeaways emerged from {company}'s latest earnings report?",
    "Financial Metrics": "What notable changes in {company}'s financial performance metrics have been reported recently?",
    "Guidance": "Has {company} revised its financial or operational guidance for upcoming periods?",
    # Corporate Strategy
    "Strategic Initiatives": "What significant strategic initiatives or business pivots has {company} announced recently?",
    "M&A Activity": "What material acquisition, merger, or divestiture activities involve {company} currently?",
    "Leadership": "What executive leadership changes have been announced at {company} recently?",
    "Contract News": "What significant contract wins, losses, or renewals has {company} recently announced?",
    "Product Launches": "What significant new product launches or pipeline developments has {company} announced?",
    # Operations
    "Operational Status": "What material operational disruptions or capacity changes is {company} experiencing currently?",
    "Supply Chain": "How are supply chain conditions affecting {company}'s operations and outlook?",
    "Production": "What production milestones or efficiency improvements has {company} achieved recently?",
    "Cost Management": "What cost-cutting measures or expense management initiatives has {company} recently disclosed?",
    # Market Position
    "Market Share": "What notable market share shifts has {company} experienced recently?",
    "Competitive Landscape": "How is {company} responding to new competitive threats or significant competitor actions?",
    "Product Development": "What significant new product launches or pipeline developments has {company} announced?",
    # External Factors
    "Regulatory Environment": "What specific regulatory developments are materially affecting {company}?",
    "Macroeconomic Impact": "How are current macroeconomic factors affecting {company}'s performance and outlook?",
    "Legal Proceedings": "What material litigation developments involve {company} currently?",
    "Industry Trends": "What industry-specific trends or disruptions are directly affecting {company}?",
    # Capital Structure
    "Capital Allocation": "What significant capital allocation decisions has {company} announced recently?",
    "Shareholder Returns": "What changes to dividends, buybacks, or other shareholder return programs has {company} announced?",
    "Debt Management": "What debt issuance, refinancing, or covenant changes has {company} recently announced?",
    "Credit Rating": "Have there been any credit rating actions or outlook changes for {company} recently?",
    # Market Sentiment
    "Investor Shifts": "What shifts in the prevailing narrative around {company} are emerging among influential investors?",
    "Upcoming Catalysts": "What significant events could impact {company}'s performance in the near term?",
    "Unusual Developments": "What unexpected disclosures or unusual trading patterns has {company} experienced recently?",
    "Activist Involvement": "Is there any activist investor involvement or significant shareholder actions affecting {company}?",
}


PROJECT_DIRECTORY = Path(__file__).parent.parent


class Settings(BaseSettings):
    # Required
    BIGDATA_API_KEY: str
    OPENAI_API_KEY: str

    # Data storage configuration
    DB_STRING: str = "sqlite:///briefs.db"
    TEMPLATES_DIR: str = str(PROJECT_DIRECTORY / "bigdata_briefs" / "templates")

    # General configuration
    WATCHLIST_ITEMS_LIMIT: int = 200
    TOPICS: dict = DEFAULT_TOPICS
    INTRO_SECTION_MIN_RELEVANCE_SCORE: int = 3
    MAX_INTRO_SECTION_COMPANIES: int = 8

    # Novelty configuration
    NOVELTY_ENABLED: bool = True
    NOVELTY_MODEL: str = "text-embedding-3-large"
    NOVELTY_THRESHOLD: float = 0.7
    NOVELTY_LOOKBACK_DAYS: int = 14
    NOVELTY_STORAGE_LOOKBACK_HOURS: int = 1
    NOVELTY_STORAGE_THRESHOLD: float = 0.8
    EMBEDDING_RETRIES: int = 3

    # Search configuration
    SDK_SIMULTANEOUS_REQUESTS: int = 80
    SDK_DOCS_LIMIT_EXPLORATORY: int = 5
    SDK_RERANK_EXPLORATORY: float = 0.8
    EXPLORATORY_SENTIMENT_THRESHOLD: float = 0.3
    SDK_DOCS_LIMIT_FOLLOWUP: int = 5
    SDK_RERANK_FOLLOWUP: float = 0.9
    FOLLOWUP_SENTIMENT_THRESHOLD: float = 0.3
    SDK_RETRIES: int = 3

    # LLM configuration
    LLM_FOLLOW_UP_QUESTIONS: int = 5
    LLM_RETRIES: int = 3

    @classmethod
    def load_from_env(cls) -> "Settings":
        return cls()


settings = Settings.load_from_env()
