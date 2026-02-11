import sys
import subprocess

# This script now executes whatever the database tells it to.
# WARNING: Full System Access Granted.
task_command = sys.argv[1]

print(f"🤖 TITAN EXECUTIONER: Running -> {task_command}")
try:
    result = subprocess.run(task_command, shell=True, check=True, capture_output=True, text=True)
    print(f"✅ SUCCESS:\n{result.stdout}")
    sys.exit(0)
except subprocess.CalledProcessError as e:
    print(f"❌ FAILED:\n{e.stderr}")
    sys.exit(1)
