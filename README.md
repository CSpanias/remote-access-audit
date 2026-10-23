# Remote-Access-Audit

A Python-based tool designed to make Remote Access security reviews more efficient.

Developed as an educational tool to accompany [Remote Access Network Security Explained](https://mollysec.com/posts/remote-access-security-explained/). 

The generated outputs are intended to support formal security reviews and can be used as inputs into downstream reporting and governance platforms.

```text
Configuration Review
        ↓
Structured Assessment
        ↓
Markdown Report + JSON Export
```

## Installation

### [UV](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) (Method 1 - Recommended)

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install remote-access-audit via UV
uv tool install git+https://github.com/CSpanias/remote-access-audit

# Verify installation
remote-access-audit -h

# Update
uv tool upgrade remote-access-audit
```

### Development Installation

> Recommended for contributors and anyone modifying the source code.
>
> The editable installation (`-e`) allows local code changes to take effect immediately without reinstalling the package.

```bash
# Clone repository
git clone https://github.com/CSpanias/remote-access-audit /opt/remote-access-audit

# Move into the directory
cd /opt/remote-access-audit

# Create virtual environment
uv venv

# Install editable package
uv pip install -e .

# Verify installation
python -m remote_access_audit.review
```

## Features

WIP

## Usage

WIP

## Example Output

WIP

## Requirements

- Python 3.11+
- UV (recommended)

## Roadmap

WIP