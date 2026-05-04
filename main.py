"""
TDD Multi-Agent Loop Controller
Orchestrates Planner → Coder → Executor feedback loop
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict
from agents import Planner, Coder, Executor, all_tests_passed

def load_task_config(task_code: str) -> Dict[str, str]:
    """Load task configuration from a JSON file based on the passed task code."""
    task = task_code.lower().strip()
    if not task:
        raise ValueError("Task code cannot be empty")

    config_path = Path("codes") / f"code_{task}.json"
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path.resolve()}"
        )

    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    goal = config.get("goal")
    test_file = config.get("test_file")
    if not isinstance(goal, str) or not goal.strip():
        raise ValueError(f"Invalid or missing 'goal' in {config_path}")
    if not isinstance(test_file, str) or not test_file.strip():
        raise ValueError(f"Invalid or missing 'test_file' in {config_path}")

    test_path = Path(test_file).expanduser()
    if not test_path.exists():
        raise FileNotFoundError(
            "Configured test file does not exist: "
            f"{test_path.resolve()} (from {config_path.resolve()})"
        )

    return {
        "goal": goal,
        "test_file": test_file,
        "output_file": f"{task}.py",
    }


class LoopController:
    """
    Orchestrates the multi-agent flow:
    1. Planner creates a plan from goal + previous test results
    2. Coder writes code following the plan
    3. Executor runs tests and captures results
    4. Loop back if tests fail (up to max iterations)
    """
    
    def __init__(self, test_module_path: str, max_iterations: int = 5):
        self.test_module_path = test_module_path
        self.max_iterations = max_iterations
        self.planner = Planner()
        self.coder = Coder()
        self.executor = Executor(test_module_path)
    
    async def run(self, goal: str) -> Dict[str, Any]:
        """
        Run the multi-agent loop.
        
        Args:
            goal: The coding task to accomplish
        
        Returns:
            Final state dict
        """
        # Initialize shared state
        state = {
            "goal": goal,
            "plan": [],
            "code": "",
            "test_results": "",
            "status": "Initialized",
            "iteration": 0
        }
        
        print("\n" + "="*70)
        print("🚀 TDD Multi-Agent System Started")
        print("="*70)
        self._log_state(state)
        
        # Main loop
        for iteration in range(1, self.max_iterations + 1):
            state["iteration"] = iteration
            print(f"\n{'='*70}")
            print(f"Iteration {iteration}/{self.max_iterations}")
            print(f"{'='*70}")
            
            # Step 1: Planner
            print("\n[1/3] Planner → Creating plan...")
            state = await self.planner(state)
            self._log_state(state)
            
            # Step 2: Coder
            print("\n[2/3] Coder → Writing code...")
            state = await self.coder(state)
            print(f"Generated code ({len(state['code'])} chars)")
            
            # Step 3: Executor
            print("\n[3/3] Executor → Running tests...")
            state = await self.executor(state)
            self._log_state(state)
            
            # Check if tests passed
            if all_tests_passed(state):
                print("\n" + "🎉 SUCCESS! All tests passed!")
                state["status"] = f"✓ All tests passed on iteration {iteration}"
                break
            else:
                print(f"\n⚠️  Tests failed. Feeding results back to planner...")
                if iteration < self.max_iterations:
                    print(f"Retrying... ({self.max_iterations - iteration} attempts remaining)")
        else:
            # Max iterations reached without passing tests
            state["status"] = f"✗ Failed to pass tests after {self.max_iterations} iterations"
            print(f"\n❌ FAILED: Max iterations ({self.max_iterations}) reached")
        
        print("\n" + "="*70)
        print("📋 Final State")
        print("="*70)
        self._log_state(state)
        
        return state
    
    def _log_state(self, state: Dict[str, Any]):
        """Pretty-print the current state."""
        print(f"\nStatus: {state.get('status', 'N/A')}")
        
        plan = state.get("plan", [])
        if plan:
            print(f"\nPlan ({len(plan)} steps):")
            for i, step in enumerate(plan, 1):
                print(f"  {i}. {step}")
        
        code = state.get("code", "")
        if code:
            lines = code.split('\n')
            print(f"\nCode ({len(lines)} lines):")
            # Show first 15 and last 5 lines
            if len(lines) <= 20:
                for line in lines:
                    print(f"  {line}")
            else:
                for line in lines[:15]:
                    print(f"  {line}")
                print(f"  ... ({len(lines) - 20} more lines) ...")
                for line in lines[-5:]:
                    print(f"  {line}")
        
        results = state.get("test_results", "")
        if results:
            print(f"\nTest Results:")
            for line in results.split('\n'):
                if line.strip():
                    print(f"  {line}")


async def main():
    """Main entry point for running the TDD system."""
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <task_code>")
        print("Example: python3 main.py lru")
        sys.exit(1)

    task_code = sys.argv[1]
    try:
        task_config = load_task_config(task_code)
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    test_path = task_config["test_file"]
    goal = task_config["goal"]
    output_file = task_config["output_file"]

    print(f"Selected task: {task_code}")
    print(f"Config goal: {goal}")
    print(f"Config test file: {test_path}")
    
    controller = LoopController(test_path)
    final_state = await controller.run(goal)
    
    # Optionally save code to file
    code = final_state.get("code", "")
    if code:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"\n✓ Generated code saved to {output_file}")
    
    return final_state

if __name__ == "__main__":
    asyncio.run(main())
