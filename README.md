# Xerxes

> An intelligent DevOps agent with BYOK (Bring Your Own Key) for managing cloud infrastructure through conversational AI.

Xerxes is a command-line AI agent that helps you manage your DevOps infrastructure using natural language. It integrates with AWS, GCP, Kubernetes, and Docker, allowing you to query, manage, and operate your infrastructure through a conversational interface.

## Features

- **Multi-Cloud Support**: AWS CLI, GCP (gcloud), Kubernetes (kubectl), Docker
- **Intelligent Agent**: Uses Vertex AI (Claude 3.5 Sonnet or Gemini) for natural language understanding
- **Safety First**: Auto-executes read-only commands, requires confirmation for destructive operations
- **Extensible Architecture**: Easy to add new tools and LLM providers
- **Rich Terminal UI**: Beautiful output with syntax highlighting and structured formatting
- **Session Management**: Maintains conversation context for multi-turn interactions

## Installation

### Using pip

```bash
pip install xerxes
```

### Using UV (Recommended)

```bash
uv tool install xerxes
```

### From Source

```bash
git clone https://github.com/yourusername/xerxes.git
cd xerxes
uv sync
```

## Prerequisites

### Required

- Python 3.10+
- GCP Project with Vertex AI API enabled
- Service account credentials or API key for Vertex AI

### Optional (Install CLI tools you want to use)

- `kubectl` for Kubernetes management
- `docker` for container operations
- `aws` CLI for AWS operations
- `gcloud` CLI for GCP operations

## Configuration

### Initial Setup

1. Set your GCP project ID:

```bash
xerxes config set vertex_project_id your-gcp-project-id
```

2. Set up authentication (choose one):

**Option A: Service Account (Recommended)**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**Option B: API Key**
```bash
xerxes config set vertex_api_key your-api-key
```

### Optional Configuration

```bash
# Change region (default: us-central1)
xerxes config set vertex_location us-east1

# Change model (default: claude-3-5-sonnet@20240620)
xerxes config set vertex_model gemini-1.5-pro

# View current config
xerxes config show
```

## Usage

### Interactive Chat

Start a conversational session:

```bash
xerxes chat
```

Example interactions:

```
You: List all pods in the production namespace

Xerxes: I'll get the pods from the production namespace.
[Executes: kubectl get pods -n production]
[Shows formatted table of pods]

You: Show me logs for the api-server pod

Xerxes: I'll fetch the logs for the api-server pod.
[Executes: kubectl logs api-server -n production]
[Shows logs]

You: Delete the failed pod

⚠️  Destructive Operation Detected
Function: kubectl_delete
Arguments:
  resource_type: pod
  name: failed-pod
  namespace: production

Confirm execution? [y/N]:
```

### Check Available Tools

```bash
xerxes tools
```

Output:
```
DevOps Tools
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Tool       ┃ CLI Command ┃ Status      ┃ Version         ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ kubernetes │ kubectl     │ ✓ Installed │ v1.28.0         │
│ docker     │ docker      │ ✓ Installed │ 24.0.5          │
│ aws        │ aws         │ ✗ Not Found │ N/A             │
│ gcp        │ gcloud      │ ✓ Installed │ 455.0.0         │
└────────────┴─────────────┴─────────────┴─────────────────┘
```

### Example Use Cases

**Kubernetes:**
- "List all running pods in production"
- "Get logs from the nginx pod"
- "Describe the frontend deployment"
- "Show me all services in the default namespace"

**Docker:**
- "List all running containers"
- "Show me the logs for container xyz"
- "What Docker images do I have?"

**AWS:**
- "List all S3 buckets"
- "Show EC2 instances in us-east-1"
- "Get CloudWatch logs for my-log-group"

**GCP:**
- "List Compute Engine instances"
- "Show me Cloud Run services"
- "List storage buckets"

## Architecture

```
xerxes/
├── agent/          # Core agent logic and chat loop
├── llm/            # LLM provider abstractions
│   └── vertex.py   # Vertex AI implementation
├── tools/          # DevOps CLI tool wrappers
│   ├── kubernetes.py
│   ├── docker.py
│   ├── aws.py
│   └── gcp.py
├── executor/       # Command execution with safety checks
└── config/         # Configuration management
```

## Safety Features

Xerxes includes built-in safety mechanisms:

1. **Destructive Operation Detection**: Automatically detects commands that modify or delete resources
2. **Confirmation Prompts**: Requires user confirmation before executing destructive operations
3. **Command Preview**: Shows exactly what will be executed before running
4. **Read-Only Auto-Execution**: Safely auto-executes read-only commands like `get`, `list`, `describe`

## Development

### Setup Development Environment

```bash
git clone https://github.com/shammianand/xerxes.git
cd xerxes
uv sync --all-extras
```

### Run Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Format code
uv run black src/

# Lint
uv run ruff check src/
```

## Roadmap

- [ ] Support for additional LLM providers (Anthropic, OpenAI, Ollama)
- [ ] Terraform integration
- [ ] Ansible playbook execution
- [ ] Multi-step workflow automation
- [ ] Session history and replay
- [ ] Web dashboard for monitoring
- [ ] Plugin system for custom tools

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details

## Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Uses [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Powered by [Vertex AI](https://cloud.google.com/vertex-ai) for LLM capabilities

## Support

For issues, questions, or contributions, please open an issue on GitHub.
