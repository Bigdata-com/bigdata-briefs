# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
