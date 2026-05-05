"""
Multi-agent TDD system components.
Each agent operates on a shared state dict.
"""
import re
import inspect
from typing import Any, Dict
from llm import llm


class Planner:
  """
  Breaks down a goal into atomic steps.
  Input: state["goal"], state["test_results"]
  Output: updates state["plan"]
  """

  async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
    goal = state.get("goal", "")
    test_results = state.get("test_results", "")

    prompt = f"""You are a planning agent. Your job is to break down a coding goal into atomic, 
sequential steps to solve it using TDD.

Goal: {goal}

Previous test results (if any):
{test_results if test_results else "No test results yet"}

Create a concise plan with 2-4 atomic steps. Each step should be a single task that can be implemented 
and tested. Do NOT include any code in the plan.

Format your response as a numbered list:
1. [step]
2. [step]
etc.

Plan:"""

    response = await llm(prompt)

    # Parse the response into a list of steps
    lines = response.strip().split('\n')
    plan = []
    for line in lines:
      # Remove numbering (1., 2., etc.) and clean up
      clean_line = re.sub(r'^[\d]+\.\s*', '', line).strip()
      if clean_line and len(clean_line) > 3:  # Filter out empty/very short lines
        plan.append(clean_line)

    state["plan"] = plan
    state["status"] = f"Planner: Generated {len(plan)} steps"

    return state


class Coder:
    """
    Writes complete, runnable code to satisfy the goal and plan.
    Input: goal + plan
    Output: updates state["code"]
    """

    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        goal = state.get("goal", "")
        plan = state.get("plan", [])
        test_results = state.get("test_results", "")

        plan_text = "\n".join(f"- {step}" for step in plan)

        prompt = f"""You are a code generation agent. Your job is to write Python code that satisfies the goal and plan.

Goal: {goal}

Plan:
{plan_text}

Previous test failures (if any):
{test_results if test_results else "No failures yet"}

Write ONLY the complete Python code needed. The code will be executed and tested.
Do not include comments explaining the code, just the implementation.
Make sure to define the main function/class that will be tested.

Code:"""
    
        response = await llm(prompt)

        # Extract code block if wrapped in markdown, otherwise use as-is
        code = response.strip()
        if code.startswith("```python"):
            code = code[9:]  # Remove ```python
        if code.startswith("```"):
            code = code[3:]  # Remove ```
        if code.endswith("```"):
            code = code[:-3]  # Remove trailing ```

        state["code"] = code.strip()
        state["status"] = f"Coder: Generated {len(state['code'])} chars of code"

        return state


class Executor:
    """
    Runs the generated code and executes test functions.
    Input: state["code"], test_results (via test_func)
    Output: updates state["test_results"]
    """

    def __init__(self, test_module_path: str):
        """
        Args:
            test_module_path: Path to the test file (e.g., "tests/test_fibonacci.py")
        """
        self.test_module_path = test_module_path

    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        code = state.get("code", "")

        # Execute the code in a namespace
        namespace = {}
        try:
            exec(code, namespace)
        except Exception as e:
            state["test_results"] = f"Execution error: {type(e).__name__}: {e}"
            state["status"] = "Executor: Code execution failed"
            return state

        # Now run tests from the test module
        try:
            # Load the test module
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_module", self.test_module_path)
            test_module = importlib.util.module_from_spec(spec)

            # Make generated code available to tests
            test_module.__dict__.update(namespace)

            spec.loader.exec_module(test_module)

            # Run all test functions
            test_results = []
            test_count = 0
            failed_count = 0

            for name in dir(test_module):
                if name.startswith("test_"):
                    test_count += 1
                    try:
                        test_func = getattr(test_module, name)

                        # Get function signature to extract parameters
                        sig = inspect.signature(test_func)
                        params = list(sig.parameters.keys())

                        # Resolve parameters from namespace (generated code)
                        args = []
                        for param in params:
                            if param in namespace:
                                args.append(namespace[param])
                            else:
                                raise ValueError(f"Parameter '{param}' not found in generated code")

                        # Call test function with resolved arguments
                        test_func(*args)
                        test_results.append(f"✓ {name}")
                    except AssertionError as e:
                        failed_count += 1
                        test_results.append(f"✗ {name}: {e}")
                    except Exception as e:
                        failed_count += 1
                        test_results.append(f"✗ {name}: {type(e).__name__}: {e}")

            result_text = "\n".join(test_results)
            state["test_results"] = result_text

            if failed_count == 0:
                state["status"] = f"Executor: All {test_count} tests passed ✓"
            else:
                state["status"] = f"Executor: {failed_count}/{test_count} tests failed"

        except Exception as e:
            state["test_results"] = f"Test loading error: {type(e).__name__}: {e}"
            state["status"] = "Executor: Test execution failed"

        return state


def all_tests_passed(state: Dict[str, Any]) -> bool:
    """Check if all tests passed."""
    results = state.get("test_results", "")
    # All tests passed if no ✗ marks
    return "✗" not in results and results


def extract_iteration_num(state: Dict[str, Any]) -> int:
    """Extract iteration number from status or return 0."""
    status = state.get("status", "")
    match = re.search(r"iteration (\d+)", status, re.IGNORECASE)
    return int(match.group(1)) if match else 0
