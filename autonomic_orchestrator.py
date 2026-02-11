import time
import subprocess
import os
from supabase import create_client

# --- CONFIG ---
URL = "https://ntbujdihrfunfxajhzhs.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YnVqZGlocmZ1bmZ4YWpoemhzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODc5NzU5OSwiZXhwIjoyMDg0MzczNTk5fQ.ZrDASOrTH81XgqAyFu7cws9Jdj7lo1BRPrbbO0imsCw"
OUTPUT_FILE = os.path.expanduser("~/lazylogic/titan_output.txt")
REPO_PATH = os.path.expanduser("~/lazylogic")

# --- THE COMMANDS ---
# 1. DEPLOY (Push to Live Site)
CMD_DEPLOY = f"cd {REPO_PATH} && git add . && git commit -m 'Titan Auto-Fix' --allow-empty && git push -u origin main --force && echo '🚀 SUCCESS: Live site is updating...'"

# 2. UPDATE (Pull upgrades for Titan itself)
CMD_UPDATE = f"cd {REPO_PATH} && git pull && ./venv/bin/pip install -r requirements.txt && echo '🔄 SYSTEM UPGRADED'"

# 3. STATUS (Check health)
CMD_STATUS = "echo '✅ ONLINE' && df -h | grep /dev/sda"

def run_worker():
    print("🦾 TITAN WORKER: Online (Smart Logic)...")
    supabase = create_client(URL, KEY)

    while True:
        try:
            # 1. FETCH TASKS
            response = supabase.table("tasks").select("*").eq("status", "pending").execute()
            tasks = response.data

            for task in tasks:
                task_id = task['id']
                raw_text = task['description'].lower().strip()
                final_cmd = raw_text # Default: run exactly what was typed

                # --- FUZZY LOGIC MATCHING ---
                # If you say "update site", "fix site", "deploy", or "push" -> WE DEPLOY.
                if any(x in raw_text for x in ["update site", "fix site", "deploy", "push", "publish"]):
                    print(f"⚡ DETECTED INTENT: DEPLOY ({raw_text})")
                    final_cmd = CMD_DEPLOY
                
                # If you say "upgrade system", "pull code" -> WE UPDATE TITAN.
                elif any(x in raw_text for x in ["upgrade", "pull", "update system"]):
                    print(f"⚡ DETECTED INTENT: UPDATE SYSTEM ({raw_text})")
                    final_cmd = CMD_UPDATE

                # If you say "status", "check" -> WE CHECK HEALTH.
                elif any(x in raw_text for x in ["status", "check", "health"]):
                     final_cmd = CMD_STATUS

                # ----------------------------

                print(f"⚡ EXECUTING: {final_cmd[:50]}...")
                supabase.table("tasks").update({"status": "processing"}).eq("id", task_id).execute()

                try:
                    # Run it
                    process = subprocess.run(final_cmd, shell=True, capture_output=True, text=True, timeout=120)
                    output = process.stdout if process.returncode == 0 else f"❌ ERROR:\n{process.stderr}"
                    if not output: output = "✅ Done."
                    status = "complete" if process.returncode == 0 else "failed"
                except Exception as e:
                    output = f"❌ CRASH: {e}"
                    status = "failed"

                # Write to local file for CLI
                with open(OUTPUT_FILE, "w") as f:
                    f.write(output)

                # Update DB
                supabase.table("tasks").update({"status": status}).eq("id", task_id).execute()
                print(f"✅ FINISHED #{task_id}")

            time.sleep(1)

        except Exception as e:
            print(f"⚠️ ERROR: {e}")
            time.sleep(2)

if __name__ == "__main__":
    run_worker()
