# Hi SDK - LLM Development Kit for Raspberry Pi

A Python SDK for interacting with LLM models on Raspberry Pi.

## Installation Options

### Option 1: Pre-built Raspberry Pi Image
Download our pre-configured Raspberry Pi image with all dependencies:
[Download Hi SDK Image](your_drive_link_here)

This is a pre-built image with all dependencies installed on a Raspberry Pi OS 6.6.31+rpt-rpi-v8.

### Option 2: Quick Setup

Prerequisites:
- Python 3.11.2 or higher
- Raspberry Pi OS

```bash
# Clone and install
git clone https://github.com/svenplb/hi-sdk.git
cd hi-sdk
pip install -e .

# Run setup (this will install Ollama, download models, and start services)
python3 -m hi setup --dev
```

After setup completes, you can start using the SDK:
```bash
hi chat  # Start chatting
hi models  # List available models
```

## Quick Start

```python
from sdk.client import HiClient

client = HiClient()
client.load_model("gemma2:2b", temperature=0.7)
response = client.chat("Tell me a joke")
print(response)
```

## Features

- Multiple model support (gemma2:2b, qwen:1.8b, qwen:0.5b)
- Streaming responses
- System prompts
- Performance metrics
- Conversation tracking
- CLI interface

## Development

The project structure:
```text
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