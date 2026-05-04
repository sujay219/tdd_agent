#!/usr/bin/env python3
"""
TDD Multi-Agent System - Entry point
Usage: python planner.py <test_file_path>
"""
import asyncio
import sys
from main import LoopController


async def main():
    # Get test file path and goal from command line
    if len(sys.argv) < 3:
        print("Usage: python planner.py <test_file_path> <goal>")
        print("Example: python planner.py tests/test_fibonacci.py 'Generate fibonacci function'")
        sys.exit(1)
    
    test_file = sys.argv[1]
    goal = sys.argv[2]

    test_name = test_file.split("/")[-1].replace(".py", "")
    goal = f"Solve the problem defined in {test_file}"

    # Run the system
    controller = LoopController(test_file, max_iterations=5)
    final_state = await controller.run(goal)
    
    # Exit with appropriate code
    if "✓" in final_state.get("status", ""):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
