import os

TEST_DATABASE_DB_STRING = "sqlite:////temp/briefs/test.db"
# Placeholder credentials, the external APIs are mocked in tests
TEST_PLACEHOLDER_CREDENTIAL = "test-placeholder"

# Override environment variables for testing
os.environ.update(
    {
        "BIGDATA_API_KEY": TEST_PLACEHOLDER_CREDENTIAL,
        "OPENAI_API_KEY": TEST_PLACEHOLDER_CREDENTIAL,
        "DB_STRING": TEST_DATABASE_DB_STRING,
        "LOG_LEVEL": "ERROR",
    }
)
