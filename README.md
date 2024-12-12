# Hi SDK - LLM Development Kit for Raspberry Pi

A Python SDK for interacting with LLM models on Raspberry Pi.

## Installation Options

### Option 1: Pre-built Raspberry Pi Image
Download our pre-configured Raspberry Pi image with all dependencies:
[Download Hi SDK Image](your_drive_link_here)

This is a pre-built image with all dependencies installed on a Raspberry Pi OS 6.6.31+rpt-rpi-v8.

### Option 2: Development Setup

Prerequisites:
- Python 3.11.2 or higher
- Raspberry Pi OS

```bash
# Clone the repository
git clone https://github.com/svenplb/hi-sdk.git
cd hi-sdk

# Create and activate virtual environment
python3 -m venv --system-site-packages venv
source venv/bin/activate

# Install in development mode
pip install -e .
```

## Quick Start

```python
from sdk.client import HiClient
from sdk.utils import SDKLogger

# Initialize client
client = HiClient()

# Load a model
client.load_model("gemma2:2b", temperature=0.7)

# Simple chat
response = client.chat("Tell me a joke")
print(response)

# Streaming chat with callback
def on_token(token):
    print(token, end="", flush=True)

client.register_callback("on_token", on_token)
for _ in client.chat("Tell me another joke"):
    pass  # Tokens handled by callback
```

## CLI Usage

After installation, you can use the CLI:

```bash
# Start interactive chat
hi chat --model gemma2:2b --temp 0.7

# List available models
hi models
```

## Features

- Multiple model support (gemma2:2b, qwen:1.8b, qwen:0.5b)
- Streaming responses
- System prompts
- Performance metrics
- Conversation tracking
- CLI interface

## Development

We suggest using a virtual environment (we preinstall all dependencies on the device at the default path `/home/hi-sdk/venv`)

The project structure:
```
hi-sdk/
├── sdk/
│   ├── __init__.py
│   ├── cli.py
│   ├── client.py
│   ├── utils.py
│   └── exceptions.py
├── examples/
│   └── quickstart.py
├── tests/
│   └── test_api.py
└── setup.py
```