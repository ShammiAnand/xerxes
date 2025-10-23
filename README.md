# Xerxes

<div align="center">

**An intelligent DevOps agent with unrestricted CLI access and free-form reasoning**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-usage) • [Contributing](#-contributing)

</div>

---

## Overview

Xerxes is a command-line AI agent that transforms natural language into DevOps operations. Unlike traditional tools with predefined commands, Xerxes uses **free-form thinking** to execute **any** command supported by your installed CLI tools (AWS, GCP, Kubernetes, Docker).

## Features

### Core Capabilities

- **Unrestricted CLI Access**: Execute ANY command from AWS CLI, gcloud, kubectl, or docker
- **Free-Form Thinking**: LLM reasons about your request and forms optimal commands
- **Interactive Approval**: See command + reasoning before execution
  - `[R]un` - Execute this command
  - `[S]kip` - Skip and continue
  - `[A]lways` - Auto-approve for session
- **Bring Your Own Key (BYOK)**: Use your own Vertex AI credentials
- **Multi-Cloud Support**: AWS, GCP, Kubernetes, Docker in one interface
- **Safety Mechanisms**: Automatic detection of destructive operations

## Installation

### Using UV (Recommended)

```bash
uv tool install xerxes
```

To update to the latest version:

```bash
uv tool upgrade xerxes
```

### From Source

```bash
git clone https://github.com/shammianand/xerxes.git
cd xerxes
uv sync
```

## Quick Start

### 1. Prerequisites

- **Python 3.10+**
- **GCP Project** with Vertex AI API enabled
- **Service Account** or API key for Vertex AI
- **Optional**: Install CLI tools you want to use (kubectl, docker, aws, gcloud)

### 2. Configuration

Create a `.env` file:

```bash
XERXES_VERTEX_PROJECT_ID=your-gcp-project-id
XERXES_VERTEX_LOCATION=us-central1
XERXES_VERTEX_MODEL=gemini-2.0-flash
XERXES_GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

Or use the CLI:

```bash
xerxes config set vertex_project_id your-gcp-project-id
xerxes config set google_application_credentials /path/to/sa.json
```

### 3. Start Chatting

```bash
xerxes chat
```

## Usage

### Example Session


https://github.com/user-attachments/assets/350d91eb-b999-4c18-aba3-52d4e430bb8e


**Operations:**
```
"Scale the api deployment to 5 replicas"
"Delete all pods in failed state"
"Create a new GCS bucket for backups"
```

## CLI Commands

```bash
# Start interactive chat
xerxes chat

# Manage configuration
xerxes config show
xerxes config set <key> <value>

# List available tools
xerxes tools

# Show version
xerxes version
```

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `XERXES_VERTEX_PROJECT_ID` | GCP project ID (required) | - |
| `XERXES_VERTEX_LOCATION` | GCP region | `us-central1` |
| `XERXES_VERTEX_MODEL` | Model name | `claude-3-5-sonnet@20240620` |
| `XERXES_GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON | - |
| `XERXES_MAX_TOKENS` | Max tokens per response | `4096` |
| `XERXES_TEMPERATURE` | LLM temperature | `0.0` |

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linters:
   ```bash
   uv run pytest
   uv run black src/
   uv run ruff check src/
   ```
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

```bash
# Clone the repo
git clone https://github.com/shammianand/xerxes.git
cd xerxes

# Install dependencies
uv sync --all-extras

# Run in development mode
uv run xerxes chat
```

## Roadmap

- [ ] Additional LLM providers (Anthropic direct, OpenAI, Ollama)
- [ ] Terraform integration
- [ ] Ansible playbook execution
- [ ] Multi-step workflow automation
- [ ] Session history save/replay
- [ ] Web dashboard for monitoring
- [ ] Plugin system for custom tools
- [ ] One-shot command mode (`xerxes run "list all pods"`)

## License

MIT License - see [LICENSE](LICENSE) for details

## Support

- **Bug Reports**: [Open an issue](https://github.com/shammianand/xerxes/issues)
- **Feature Requests**: [Start a discussion](https://github.com/shammianand/xerxes/discussions)
- **Documentation**: Coming soon

---

<div align="center">

**Built with ❤️ by [Shammi Anand](https://github.com/shammianand)**

</div>
