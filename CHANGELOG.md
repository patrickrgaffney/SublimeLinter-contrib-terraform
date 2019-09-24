# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Fixed

- Links in install.txt are now correct.

## v0.2.0 - 2019-09-23

### Added

- Linter now works on nested directories with `.tf` files. Previously only worked at the project folder level.

### Changed

- Use `LintMatch.error_type` property to report severity.

### Fixed

- Fix a bug where using the filename and project folder to create an absolute path would result in an invalid path.

## v0.1.0 - 2019-09-21

Initial release.
