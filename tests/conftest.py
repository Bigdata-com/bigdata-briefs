import os

TEST_DATABASE_DB_STRING = "sqlite:////temp/briefs/test.db"

# Override environment variables for testing
os.environ.update(
    {
        "BIGDATA_API_KEY": "fake-key",
        "OPENAI_API_KEY": "fake-key",
        "DB_STRING": TEST_DATABASE_DB_STRING,
    }
)