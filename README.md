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

### Option 3: Manual Setup (Without Image)

If you prefer to set up dependencies manually on your existing system:

1. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip git
```

2. Install Ollama (LLM backend):
```bash
curl https://ollama.ai/install.sh | sh
ollama pull gemma:2b
```

3. Clone and set up the SDK:
```bash
git clone https://github.com/svenplb/hi-sdk.git
cd hi-sdk
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

4. Run Ollama on new terminal:
```bash
ollama serve
```

5. Start the API server on new terminal:
```bash
python3 -m uvicorn main:app --reload
```

Now you can use the SDK as shown in the Quick Start section.

## Quick Start

```python
from sdk.client import HiClient

client = HiClient()
client.load_model("qwen:1.8b", temperature=0.7)
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
