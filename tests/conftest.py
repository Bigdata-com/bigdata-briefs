import os

TEST_DATABASE_DB_STRING = "sqlite://"

# Override environment variables for testing
os.environ.update(
    {
        "OPENAI_API_KEY": "fake-key",
        "DB_STRING": TEST_DATABASE_DB_STRING,
        "LOG_LEVEL": "ERROR",
    }
)
