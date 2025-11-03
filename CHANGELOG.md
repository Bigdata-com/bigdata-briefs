# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0.0] - Unreleased

### Added
- Added support for the new search API instead of the SDK for retrieval, allowing for more flexible queries and better performance.
- Added rate limiting and retry logic to handle API rate limits gracefully, avoiding rate limit errors.
- Added an option to disable the introduction section in the generated report, useful for large watchlists where the introduction may not be relevant or may overload the context of an LLM.

### Changed
- Fixed Pydantic model field examples to use `examples` instead of `example` to avoid deprecation warnings.

### Fixed
- Fixed issue when input was a list of companies instead of a watchlist ID.

## [3.1.2] - 2025-10-21

### Fixed
- Fixed issue where the logo link in the navbar did not preserve the access token in the URL.

## [3.1.1] - 2025-10-10

### Fix
- Buttons Generate Brief and See Example made of equal size

## [3.1.0] - 2025-10-10

### Added
- Added example at db initialization
- Improved FE

### Changed
- Modified topics list to be more user friendly
- JS scripts moved to static/scripts/
- Modified default watchlists

## [3.0.0] - 2025-09-30

### Added
- Added new models to separate `RetrievedSources` from `ReportedSources`, allowing to keep track of all retrieved sources while only including the used ones in the final report.
- Allow `topics` guiding the brief generation to be specified as part of the input JSON payload to `/briefs/create`. The default topics are still configurable via the `TOPICS` environment variable, however they are now a list of strings instead of a dictionary (Keys where never used previously).
- Allow brief reports to be generated for a specific list of entities provided as a list of entity IDs in the request payload to `/briefs/create`. This is done by providing a list of entity IDs in the `companies` field instead of a watchlist ID. The `companies` field can now accept either a watchlist ID (string) or a list of entity IDs.
- Allow the parameter `sources` to specify a whitelist of sources to be used for the brief generation. They need to be provided as a list of RavenPack source IDs, to find more information about how to get the source IDs please refer to the [Bigdata.com documentation on how to find sources](https://docs.bigdata.com/how-to-guides/search_with_specific_sources) that match your requirements or pick a handmade list of your trusted resources.

### Changed
- Changed endpoints to be asynchronous. `/briefs/create` will now return a `request_id` immediately, and progress updated and the result can be fetched later using `/briefs/status/{request_id}`.
- Changed `/briefs/create` endpoint from `GET` to `POST`, receiving the parameters in the request body as JSON.
- Simplified the tables for the source metadata into the main report. If you have a previous database, it is recommended to delete it and start fresh.
- Renamed `watchlist_id` to `companies` to better reflect that a list of entity IDs are accepted as well.

## [2.1.0] - 2025-09-11

### Added
- Added optional access token protection for the API endpoints. If the `ACCESS_TOKEN` environment variable is set, all API requests must include a `token` query parameter with the correct value to be authorized.

## [2.0.0] - 2025-08-11

### Added
- Improved UI to support human readable reports.

### Changed
- [Breaking changes] Changed output format of brief generation to facilitate easier consumption by downstream systems.


## [1.0.2] - 2025-07-25

### Added
- Health check endpoint at `/health` to verify service status.
- Dockerfile now includes a health check to ensure the service is running correctly.
- Removed setuid and setgid from all binaries in the Dockerfile to enhance security.

### Fixed
- Fixed database storage not being initialized when runned as a docker.

## [1.0.1] - 2025-07-25

### Fixed
- Hardening the docker image by ensuring up-to-date dependencies and security patches and running as non-root.

## [1.0.0] - 2025-07-24

### Added
- Initial release of the Bigdata Briefs Service Python package and image.
