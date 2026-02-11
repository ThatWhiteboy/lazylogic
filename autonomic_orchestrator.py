import time
import subprocess
import os
from supabase import create_client

# --- CONFIG ---
URL = "https://ntbujdihrfunfxajhzhs.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YnVqZGlocmZ1bmZ4YWpoemhzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODc5NzU5OSwiZXhwIjoyMDg0MzczNTk5fQ.ZrDASOrTH81XgqAyFu7cws9Jdj7lo1BRPrbbO0imsCw"
OUTPUT_FILE = os.path.expanduser("~/lazylogic/titan_output.txt")

# --- THE DICTIONARY (TEACHING IT ENGLISH) ---
COMMAND_MAP = {
    "deploy": "cd /home/thatwhiteboy/lazylogic && git add . && git commit -m 'Titan Auto-Deploy' && git push origin main && echo '🚀 DEPLOY SENT: Code pushed to GitHub. Live site updating in 60s.'",
    "status": "echo '✅ SYSTEM ONLINE' && df -h | grep /dev/sda && echo '--- MEMORY ---' && free -h",
    "backup": "cd /home/thatwhiteboy/lazylogic && python3 titan-backup.py && echo '💾 BACKUP COMPLETE: Saved to ~/lazylogic/backups'",
    "update": "cd /home/thatwhiteboy/lazylogic && git pull && ./venv/bin/pip install -r requirements.txt && echo '🔄 SYSTEM UPDATED'",
    "kill": "pkill -f chrome && pkill -f firefox && echo '💀 BROWSERS KILLED'"
}

def run_worker():
    print("🦾 TITAN WORKER: Online (Smart Mode)...")
    supabase = create_client(URL, KEY)

    while True:
        try:
            # 1. FETCH TASKS
            response = supabase.table("tasks").select("*").eq("status", "pending").execute()
            tasks = response.data

            for task in tasks:
                task_id = task['id']
                raw_command = task['description'].lower().strip()
                
                # TRANSLATE ENGLISH -> BASH
                # If the word is in our dictionary, use the complex command.
                # If not, just run what you typed.
                final_command = COMMAND_MAP.get(raw_command, task['description'])

                print(f"⚡ RUNNING: {raw_command} -> {final_command[:20]}...")

                supabase.table("tasks").update({"status": "processing"}).eq("id", task_id).execute()

                try:
                    process = subprocess.run(final_command, shell=True, capture_output=True, text=True, timeout=60)
                    output = process.stdout if process.returncode == 0 else f"❌ ERROR:\n{process.stderr}"
                    if not output: output = "✅ Done (No output)."
                    status = "complete" if process.returncode == 0 else "failed"
                except Exception as e:
                    output = f"❌ CRASH: {e}"
                    status = "failed"

                with open(OUTPUT_FILE, "w") as f:
                    f.write(output)

                try:
                    if task.get('bot_id'):
                        supabase.table("audit_logs").insert({
                            "bot_id": task['bot_id'], "raw_response": output, "outcome_success": (status == "complete")
                        }).execute()
                except:
                    pass

                supabase.table("tasks").update({"status": status}).eq("id", task_id).execute()
                print(f"✅ FINISHED #{task_id}")

            time.sleep(1)

        except Exception as e:
            print(f"⚠️ ERROR: {e}")
            time.sleep(2)

if __name__ == "__main__":
    run_worker()
