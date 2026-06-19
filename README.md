# SOCA - Sutra-Oriented Cognitive Architecture

> A provenance-aware, self-verifying cognitive system for resource-constrained reasoning

## Overview

SOCA is a cognitive architecture that replaces monolithic neural models with a graph-based execution engine of composable, executable knowledge units (Sutras). It features:

- **Executable Knowledge Kernels**: Sutras as composable, verifiable, versioned functions
- **Verification-Driven Generation**: Generate → Test → Repair loop
- **Layered Memory**: Non-destructive, hierarchical memory (Kosha-Net)
- **End-to-End Explainability**: Complete execution traces with provenance

## Status: ✅ Prototype Ready

SOCA Runtime v0.1 is running on **Android (Termux)** with 6 core Sutras and full dependency scheduling working.

## Core Sutras

| Sutra | Description | Status |
|-------|-------------|--------|
| `sutra_001` | Integer Addition | ✅ |
| `sutra_003` | Integer Multiplication | ✅ |
| `sutra_005` | Integer Comparison | ✅ |
| `sutra_008` | Dependency Sort (Topological) | ✅ |
| `sutra_009` | Schedule Task (Parallel) | ✅ |
| `sutra_010` | Verify Output | ✅ |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/divineearthly/SOCA-Core.git
cd SOCA-Core

# Register sutras
python register_sutras.py

# Run tests
python test_runtime.py
```

Example: Dependency Scheduling

```python
from runtime.soca_runtime import SOCARuntime

runtime = SOCARuntime()

# Define a dependency graph
graph = {
    "nodes": ["A", "B", "C", "D"],
    "edges": [["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"]]
}

# Solve: schedule tasks in parallel
result = runtime.solve_sequence(
    ["sutra_008", "sutra_009", "sutra_010"],
    {"graph": graph, "expected": {"schedule": [["A"], ["B", "C"], ["D"]]}}
)

print(result['outputs']['schedule'])
# Output: [['A'], ['C', 'B'], ['D']]
```

Performance

· Memory Usage: < 50 MB RAM
· Platform: Android (Termux), Linux, macOS
· Language: Python 3.11+

Research Status

SOCA is a research prototype with these validated claims:

Claim Status
Executable knowledge kernels ✅ Proven
DAG-based execution ✅ Proven
Complete execution traces ✅ Proven
Dependency scheduling ✅ Proven
Verification-driven generation 🔨 In progress
Continual learning 🔨 Planned
Hybrid SOCA + LLM 🔨 Planned

Next Milestones

1. ✅ SOCA Runtime v0.1 - Dependency scheduling
2. 🔨 Stage 1: Verified Code Generation
3. 🔨 Stage 2: Hybrid SOCA + LLM
4. 🔨 Stage 3: Continual Learning
5. 🔨 Stage 4: Autonomous Sutra Evolution

License

MIT

Architecture

```
User Query
    │
    ▼
[ Samyama Router ] → Retrieve Sutras
    │
    ▼
[ Inference Graph ] → Build DAG
    │
    ▼
[ Sutra Execution ] → Execute & Trace
    │
    ▼
[ Pramana Verifier ] → Verify Output
    │
    ▼
[ Pratyabhijna Loop ] → Repair if needed
```

Contributing

SOCA is an open research project. Contributions welcome!

---

Built with ❤️ on a Redmi 14C 5G in Termux
