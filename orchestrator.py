import subprocess
import sys


tasks = [
    ["echo", "Starting orchestration"],
    [sys.executable, "src/fetch_data.py"],
    [sys.executable, "src/transform.py"],
    [sys.executable, "src/load.py"],
    [sys.executable, "src/format_for_dashboard.py"],
    ["echo", "Data updated."]
]


def run_orchestrator(task_list):
    for cmd in task_list:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, text=True)
        
            
        if result.returncode != 0:
            print(f"Error: Command failed with code {result.returncode}")
            print(result.stderr)
            sys.exit(result.returncode)

if __name__ == "__main__":
    run_orchestrator(tasks)