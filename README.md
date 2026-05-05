# 🧠 TDD Multi-Agent Coding System

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: unformatted](https://img.shields.io/badge/code%20style-minimal-brightgreen)](#)

A minimal multi-agent system that writes code using **Test-Driven Development (TDD)**.  
You provide tests → the system iteratively writes code until all tests pass.

---

## 🚀 Goal

- Automate coding using a **test-first approach**
- Ensure correctness via continuous test execution
- Keep system simple, deterministic, and reproducible

**Non-goals**
- No autonomous browsing
- No unsafe system execution
- No long memory or chat history

---

## 🏗️ Architecture

```
Tests → Planner → Coder → Executor → [Loop: Feedback if failed]
```

### Shared State Dict

All agents operate on a single state dictionary:

```python
{
  "goal": str,                # The coding task
  "plan": list[str],          # Steps to achieve goal
  "code": str,                # Generated Python code
  "test_results": str,        # Test execution output
  "status": str,              # Current status message
  "iteration": int            # Loop iteration number
}
```

### Components

#### 1. **Planner** (`agents.Planner`)
- **Input**: `state["goal"]`, `state["test_results"]`
- **Output**: `state["plan"]` (list of atomic steps)
- **Rules**:
  - No code, only steps
  - Break goal into 3-5 atomic tasks
  - Feed test failures back to create recovery plan

#### 2. **Coder** (`agents.Coder`)
- **Input**: `state["goal"]`, `state["plan"]`
- **Output**: `state["code"]` (complete runnable Python)
- **Rules**:
  - Generates complete, executable code
  - Overwrites previous code
  - Follows plan strictly

#### 3. **Executor** (`agents.Executor`)
- **Input**: `state["code"]`, test module path
- **Output**: `state["test_results"]` (pass/fail with details)
- **Rules**:
  - Executes generated code
  - Runs all `test_*` functions from test module
  - Captures stdout, stderr, exceptions
  - Updates test results with ✓/✗ marks

#### 4. **Loop Controller** (`main.LoopController`)
- **Flow**: Planner → Coder → Executor
- **Feedback**: If tests fail, feed results back to Planner
- **Termination**: Success when all tests pass OR max 5 iterations reached
- **No direct agent communication**: All via shared state dict

---

## 📁 File Structure

```
tdd_agent/
├── README.md              # This file
├── LICENSE                # MIT License
├── src/
│   ├── main.py            # CLI entry point + LoopController
│   ├── llm.py             # LLM interface (Ollama)
│   ├── agents.py          # Planner, Coder, Executor classes
│   └── planner.py         # Legacy entry point (deprecated)
├── codes/                 # Task configuration JSONs
│   ├── code_lru.json      # LRU cache task config
│   └── code_fibonacci.json # Fibonacci task config
└── tests/
    ├── test_fibonacci.py  # Example test (fibonacci series)
    └── test_lru.py        # Example test (LRU cache)
```

---

## 🔧 Setup

### Prerequisites
- Python 3.11+
- **Ollama** running locally (http://localhost:11434)
- Model: `qwen2.5:7b` or `qwen2.5-coder-14b` (configurable)

### Install Ollama

1. Download: https://ollama.ai
2. Start server:
   ```bash
   ollama serve
   ```
3. In another terminal, pull a model:
   ```bash
   ollama pull qwen2.5:7b
   # Or for better code generation:
   ollama pull qwen2.5-coder-14b
   ```

### Install Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows

# Install dependencies
pip install httpx
```

---

## 🚀 Usage

### Quick Start

The system reads task configuration from JSON files in `codes/` directory.

```bash
# Run fibonacci task
python3 src/main.py fibonacci

# Run LRU cache task
python3 src/main.py lru
```

This will:
1. Read the task configuration from `codes/code_<task>.json`
2. Extract the goal and test file path
3. Run the multi-agent loop (max 5 iterations)
4. Save generated code to `<task>.py`
5. Output formatted state after each step

### Expected Output

```
======================================================================
🚀 TDD Multi-Agent System Started
======================================================================

Status: Initialized
...

======================================================================
Iteration 1/5
======================================================================

[1/3] Planner → Creating plan...
Status: Planner: Generated 4 steps

Plan (4 steps):
  1. Start with base cases for n=0 and n=1
  2. Implement the fibonacci recurrence relation
  3. Use iteration instead of recursion for efficiency
  4. Return the series as a list

[2/3] Coder → Writing code...
Generated code (342 chars)

[3/3] Executor → Running tests...
Status: Executor: All 2 tests passed ✓

🎉 SUCCESS! All tests passed!

======================================================================
📋 Final State
======================================================================

Status: ✓ All tests passed on iteration 1
Plan (4 steps):
  ...
Test Results:
  ✓ test_fibonacci_series_first_ten_numbers
  ✓ test_fibonacci_series_edge_cases
```

---

## 🔌 LLM Configuration

The system uses **Ollama** (default: `qwen2.5:7b`).

Override via environment variables:

```bash
# Use different Ollama URL (default: http://localhost:11434/api/generate)
export OLLAMA_URL="http://ollama.example.com:11434/api/generate"

# Use different model
export OLLAMA_MODEL="qwen2.5-coder-14b"

# Control max output tokens (default: 1024)
# Increase this for longer, more complete code generation
export OLLAMA_NUM_PREDICT="2048"

# Now run tasks
python3 src/main.py fibonacci
```

### Troubleshooting Incomplete Code

If generated code is truncated (e.g., `if __name`), increase `OLLAMA_NUM_PREDICT`:

```bash
export OLLAMA_NUM_PREDICT=1024
python3 src/main.py fibonacci
```

Check logs for `done_reason=length` to confirm truncation occurred.

---

## 📝 Adding Custom Tasks

### Step 1: Create Test File

Create a new test file in `tests/`:

```python
# tests/test_my_feature.py

def _my_function(x):
    # Implementation will be generated by Coder
    pass

def test_basic():
    assert _my_function(5) == expected_result

def test_edge_case():
    assert _my_function(0) == expected_edge_result
```

### Step 2: Create Task Config JSON

Create a config file in `codes/`:

```json
// codes/code_my_feature.json
{
  "goal": "Generate a function that does X, Y, and Z. Handle edge cases.",
  "test_file": "tests/test_my_feature.py"
}
```

### Step 3: Run

```bash
python3 src/main.py my_feature
```

This will:
1. Read `codes/code_my_feature.json`
2. Load goal and test file path
3. Generate code and save to `my_feature.py`

---

## 🔄 How It Works: Example Flow

### Iteration 1

1. **Planner** reads:
   - Goal: "Generate a fibonacci series up to n numbers"
   - Test results: "" (empty, first iteration)
   - Outputs 4-step plan

2. **Coder** reads:
   - Goal + plan
   - Generates Python function `_fibonacci_series(n)`

3. **Executor**:
   - Runs generated code
   - Executes `test_fibonacci_series_first_ten_numbers()`
   - Executes `test_fibonacci_series_edge_cases()`
   - Returns: "✓ test_...\n✓ test_..."

4. **Loop Controller** checks: All tests passed? → **YES** → Done! ✓

### Iteration N (if tests fail)

1. **Planner** reads:
   - Goal: Same
   - Test results: "✗ test_foo: AssertionError: [0, 1, 1, 2] != [0, 1, 1, 2, 3]"
   - Outputs revised plan to fix the bug

2. **Coder** reads:
   - Goal + revised plan
   - Generates fixed code

3. **Executor**:
   - Tests run again
   - Returns new results

4. **Loop Controller** checks: Pass? → Try again (max 5 iterations)

---

## 💡 Design Principles

### Deterministic
- No randomness or external state
- Same input → same behavior (modulo LLM randomness)

### Modular
- Each agent is independent
- All communication via state dict
- Easy to swap agents or test components

### Simple
- ~500 lines total (agents + controller)
- No frameworks, just async/await
- Clear separation of concerns

### Testable
- Tests drive implementation
- Easy to add new test cases
- Clear feedback loop

---

## 🐛 Troubleshooting

### Connection refused to Ollama
- Make sure Ollama is running: `ollama serve`
- Check URL: `echo $OLLAMA_URL` (default: `http://localhost:11434/api/generate`)
- Check model: `ollama list` (should have `qwen2.5-coder-14b`)

### Tests not recognized
- Test functions must start with `test_` prefix
- Function being tested should be named with `_` prefix (e.g., `_fibonacci_series`)
- Executor injects generated code into test module namespace

### Infinite retry loop
- System stops after 5 iterations max
- Check LLM output: `state["code"]` might be malformed
- Check test functions: Make sure they're actually assertions, not just procedures

### LLM timeouts
- Network issue or Ollama server overloaded
- Try smaller model: `export OLLAMA_MODEL="qwen:7b"`
- Increase timeout: Modify `src/llm.py` `timeout = 300.0` (default: 180s)

### Truncated code generation
- Check `done_reason` in logs. If `done_reason=length`, token limit was hit
- Increase `OLLAMA_NUM_PREDICT`: `export OLLAMA_NUM_PREDICT=4096`
- Use a more capable model: `export OLLAMA_MODEL="qwen2.5-coder-14b"`

---

## 📊 State Flow Diagram

```
START
  ↓
[Planner] → plan, status ↓ test_results
  ↓
[Coder] → code, status ↓
  ↓
[Executor] → test_results, status ↓
  ↓
All tests passed? 
  ├─ YES → END ✓
  └─ NO → Iteration < 5?
       ├─ YES → [Planner] (loop back)
       └─ NO → END ✗
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-improvement`)
3. Add tests for new functionality
4. Commit with clear messages
5. Push and open a Pull Request

### Ideas for Contribution

- Support additional LLM backends (OpenAI, Anthropic, etc.)
- Implement agent memory/history for context across iterations
- Add code validation (AST parsing, type checking, linting)
- Support additional test frameworks (pytest, unittest)
- Optimize token usage and generation speed
- Add web UI for task management

---

## 📄 License

MIT — See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Ollama](https://ollama.ai) and [httpx](https://www.python-httpx.org/)
- Inspired by multi-agent code generation and TDD principles
