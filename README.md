# VPN-Audit

A Python-based tool designed to make Virtual Private Network security reviews more efficient.

Developed as an educational tool to accompany [Virtual Private Network Security Explained: Always On VPN](https://mollysec.com/posts/vpn-security-explained/). 

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

# Install vpn-audit via UV
uv tool install git+https://github.com/CSpanias/vpn-audit

# Verify installation
vpn-audit -h

# Update
uv tool upgrade vpn-audit
```

### Development Installation

> Recommended for contributors and anyone modifying the source code.
>
> The editable installation (`-e`) allows local code changes to take effect immediately without reinstalling the package.

```bash
# Clone repository
git clone https://github.com/CSpanias/vpn-audit /opt/vpn-audit

# Move into the directory
cd /opt/vpn-audit

# Create virtual environment
uv venv

# Install editable package
uv pip install -e .

# Verify installation
python -m vpn_audit.review
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