# Motor/App Data Contract

The integration contract is defined in code, not prose:

- `scrum_agent/core/schema.py`: `TypedDict` contract for every field returned by `build_demo_state()`.
- `docs/data_contract/demo_state.example.json`: complete JSON example generated from `build_demo_state()` with all 3 projects, 15 team members, backlog items, sprint plans, allocations, risks, and insights.

App Team mock usage:

```python
import json
from pathlib import Path

MOCK_STATE = json.loads(
    Path("docs/data_contract/demo_state.example.json").read_text(encoding="utf-8")
)
```

Runtime usage:

```python
from scrum_agent.services.demo_state import build_demo_state

state = build_demo_state()
```

Optional LLM analysis:

```python
from scrum_agent.services.agent_orchestrator import build_agent_state

state = build_agent_state(mode="auto")
```

`build_agent_state()` preserves the deterministic fields from `build_demo_state()` and adds:

- `agent_analysis`
- `recommendations`
- `approval_queue`
- `llm_metadata`
