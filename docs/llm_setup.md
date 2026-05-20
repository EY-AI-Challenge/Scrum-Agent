# Local LLM Setup

The Scrum Agent has two public entry points:

- `build_demo_state()`: deterministic motor used by the frontend contract.
- `build_agent_state()`: deterministic motor plus optional LLM analysis, recommendations, and pending approval actions.

The LLM never mutates `backlog_items`, `sprint_plans`, or `allocations` directly. It only proposes actions in `approval_queue`.

## Ollama Local Demo

Install Ollama on the Windows host, then pull a small model:

```powershell
winget install --id Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
ollama --version
ollama pull llama3.2:3b
ollama run llama3.2:3b "Resume em 3 pontos o papel de um Scrum Master."
```

Validate the local API:

```powershell
curl http://localhost:11434/api/tags
```

Configure the Scrum Agent:

```bash
export SCRUM_AGENT_LLM_PROVIDER=ollama
export SCRUM_AGENT_LLM_MODEL=llama3.2:3b
export SCRUM_AGENT_LLM_BASE_URL=http://localhost:11434
```

If WSL cannot reach `localhost:11434`, use the Windows host IP from WSL:

```bash
export WINDOWS_HOST_IP=$(ip route | awk '/default/ {print $3}')
export SCRUM_AGENT_LLM_BASE_URL=http://$WINDOWS_HOST_IP:11434
```

Run:

```bash
python3 -m scrum_agent.services.agent_orchestrator
```

## Offline Fallback

This always works without Ollama or API keys:

```python
from scrum_agent.services.agent_orchestrator import build_agent_state

state = build_agent_state(mode="offline")
```

## Future OpenAI Provider

The provider is already wired for a future API key flow:

```bash
export SCRUM_AGENT_LLM_PROVIDER=openai
export SCRUM_AGENT_LLM_MODEL=gpt-5.5
export OPENAI_API_KEY=...
```

Runtime usage stays the same:

```python
from scrum_agent.services.agent_orchestrator import build_agent_state

state = build_agent_state(mode="auto")
```
