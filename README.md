# Briefs with Bigdata.com
This repository contains a docker image for running a brief generating service using Bigdata.com SDK.


## Prerequisites
- A [Bigdata.com](https://bigdata.com) account that supports programmatic access.
- A Bigdata.com API key, which can be obtained from your account settings.
    - For more information on how to get an API key, refer to the [Bigdata.com documentation](https://docs.bigdata.com/api-reference/introduction#api-key-beta).
- A watchlist ID with the list of companies you want to generate briefs for.
    - A watchlist can be created using the [Bigdata.com SDK](https://docs.bigdata.com/getting-started/watchlist_management) or through the app @ https://app.bigdata.com/watchlists.


# Quickstart
To quickly get started, you can run the following command to build and run the docker image:
```bash
docker run -d \
  --name bigdata_briefs \
  -p 8000:8000 \
  -e BIGDATA_API_KEY=<bigdata-api-key-here> \
  -e OPENAI_API_KEY=<openai-api-key-here> \
  ghcr.io/bigdata-com/bigdata-briefs:latest
```
This will start the brief service locally on port 8000. You can then access the service @ `http://localhost:8000/` and the documentation for the API @ `http://localhost:8000/docs`.


## How to use? Generate a brief for your Bigdata.com watchlist

A brief is a executive summary of finantially relevant information about a set of companies that form your watchlist.

### Using the UI
There is a very simple UI available @ `http://localhost:8000/`.

Set your watchlist ID, the relevant dates for your report and whether you want to filter the brief
only to novel information based on previously generated briefs and click on the "Generate Brief" button.

### Programmatically
You can generate a brief by sending a POST request to the `/briefs/create` endpoint with the required
parameters. For example, using `curl`:
```bash
curl -X 'GET' \
  'http://localhost:8000/briefs/create?watchlist_id=672c2d70-2062-4330-a0a7-54c598f231db&report_start_date=2024-01-01&report_end_date=2024-01-31&novelty=true' \
  -H 'accept: application/json'
```

For more details on the parameters, refer to the API documentation @ `http://localhost:8000/docs`.


# Install and for development locally
```bash
uv sync --dev
```

To run the service, you need an API key from Bigdata.com set on the environment variable `BIGDATA_API_KEY` and additionally provide an API key from a supported LLM provider, for now OpenAI.
```bash
# Set environment variables
export BIGDATA_API_KEY=<bigdata-api-key-here>
export OPENAI_API_KEY=<openai-api-key-here>
```

Then, the following command will start the brief service locally on port 8000.
```bash
uv run -m bigdata_briefs
```

# Build and run the docker image
To build the docker image, run:
```bash
docker build -t bigdata_briefs .
```

To run the docker image, you need you can pass the required environment variables. For example:
```bash
docker run -d \
  --name bigdata_briefs \
  -p 8000:8000 \
  -e BIGDATA_API_KEY=<bigdata-api-key-here> \
  -e OPENAI_API_KEY=<openai-api-key-here> \
  bigdata_briefs
```

Alternative, pass the environment variables in a `.env` file and use the `--env-file` option.
```bash
docker run -d \
  --name bigdata_briefs \
  -p 8000:8000 \
  --env-file .env \
  bigdata_briefs
```


## Linting and formatting
This project uses [ruff](https://docs.astral.sh/ruff/) for linting and black for formatting. To ensure your code adheres to the project's style guidelines, run the following commands before committing your changes:
```bash
make lint
make format
```
