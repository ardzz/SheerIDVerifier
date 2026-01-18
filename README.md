<div align="center">

# SheerID Verifier

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/ardzz/SheerIDVerifier/actions/workflows/ci.yml/badge.svg)](https://github.com/ardzz/SheerIDVerifier/actions/workflows/ci.yml)

**A Python CLI tool for automated Google One (Gemini) student verification via SheerID API**

[Features](#-features) | [Installation](#-installation) | [Usage](#-usage) | [Development](#-development)

</div>

---

## Features

- **Modern Python Packaging** - Built with [uv](https://docs.astral.sh/uv/) for fast dependency resolution
- **Proxy Support** - SOCKS5 and HTTP proxy support via httpx
- **Rich Console Output** - Colored status messages, progress indicators, and formatted tables
- **Anti-Detection** - Browser fingerprint generation, user-agent rotation, request delays
- **Statistics Tracking** - JSON-persisted success/failure rates per university
- **Document Generation** - Auto-generates transcripts and student ID cards using Pillow

## Requirements

- Python 3.11, 3.12, or 3.13
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

## Installation

### Using uv (Recommended)

```bash
# Install uv if not already installed
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/ardzz/SheerIDVerifier.git
cd SheerIDVerifier
uv sync
```

### Using pip

```bash
git clone https://github.com/ardzz/SheerIDVerifier.git
cd SheerIDVerifier
pip install -e .
```

## Usage

### Basic Verification

```bash
# Using uv
uv run sheerid "https://services.sheerid.com/verify/...?verificationId=abc123"

# Or if installed globally
sheerid "https://services.sheerid.com/verify/...?verificationId=abc123"
```

### With Proxy

```bash
# SOCKS5 proxy
uv run sheerid --proxy socks5://localhost:1080 "https://..."

# SOCKS5 with authentication
uv run sheerid --proxy socks5://user:pass@host:1080 "https://..."

# HTTP proxy
uv run sheerid --proxy http://proxy.example.com:8080 "https://..."

# HTTP proxy with authentication
uv run sheerid --proxy http://user:pass@host:port "https://..."
```

### CLI Options

```
Usage: sheerid [OPTIONS] [URL]

Options:
  -h, --help     Show help message
  --proxy URL    Proxy server URL (http://, socks5://)
  --quiet, -q    Suppress progress output
  --version, -V  Show version number
```

### Interactive Mode

If no URL is provided, the tool prompts for input:

```bash
uv run sheerid
# Enter verification URL: [paste URL here]
```

## How It Works

1. **Link Validation** - Checks if the SheerID verification link is valid and not already used
2. **Student Data Generation** - Creates realistic student profile using Faker
3. **University Selection** - Weighted random selection from configured universities
4. **Document Generation** - Creates transcript or student ID card image
5. **API Submission** - Submits student info and uploads document to SheerID

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/ardzz/SheerIDVerifier.git
cd SheerIDVerifier

# Install with dev dependencies
uv sync --all-extras
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=sheerid_verifier

# Run specific test file
uv run pytest tests/unit/test_document.py -v
```

### Linting & Formatting

```bash
# Check linting
uv run ruff check .

# Auto-fix linting issues
uv run ruff check . --fix

# Format code
uv run ruff format .
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `httpx[socks]` | HTTP client with SOCKS5 proxy support |
| `rich` | Terminal formatting and progress bars |
| `Pillow` | Document image generation |
| `fake-useragent` | User-Agent string rotation |
| `faker` | Realistic student data generation |
| `curl_cffi` | (Optional) Better TLS fingerprinting |

## Troubleshooting

### SOCKS5 proxy not working?

```bash
# Ensure httpx[socks] is installed
uv add httpx[socks]
```

### SSL/TLS errors?

```bash
# Install curl_cffi for better TLS fingerprinting
uv add curl_cffi
```

### Rate limited?

- The tool includes random delays between requests
- Use proxy rotation for multiple verifications
- Wait before retrying after failures

## Disclaimer

This tool is for educational purposes only. Use responsibly and in accordance with SheerID's terms of service.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Made with Python by <a href="https://github.com/ardzz">Reky</a>
</div>
