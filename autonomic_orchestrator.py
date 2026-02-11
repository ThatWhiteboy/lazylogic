import time
import subprocess
import os
from supabase import create_client

# --- CONFIG ---
URL = "https://ntbujdihrfunfxajhzhs.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YnVqZGlocmZ1bmZ4YWpoemhzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODc5NzU5OSwiZXhwIjoyMDg0MzczNTk5fQ.ZrDASOrTH81XgqAyFu7cws9Jdj7lo1BRPrbbO0imsCw"
REPO_PATH = os.path.expanduser("~/lazylogic")
OUTPUT_FILE = os.path.expanduser("~/lazylogic/titan_output.txt")

# --- THE AUTOMATION ENGINE ---
def run_command(cmd):
    try:
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
        return process.stdout if process.returncode == 0 else f"❌ ERROR:\n{process.stderr}"
    except Exception as e:
        return f"❌ CRASH: {e}"

def run_worker():
    print("🦾 TITAN AUTOPILOT: Initializing...")
    supabase = create_client(URL, KEY)

    while True:
        try:
            response = supabase.table("tasks").select("*").eq("status", "pending").execute()
            tasks = response.data

            for task in tasks:
                task_id = task['id']
                raw_text = task['description'].lower().strip()
                
                # --- AUTOMATED DEPLOY LOGIC ---
                if any(x in raw_text for x in ["deploy", "update site", "live"]):
                    print(f"🚀 AUTONOMOUS DEPLOY STARTING...")
                    # Phase 1: Local Save
                    run_command(f"cd {REPO_PATH} && git add . && git commit -m 'Titan Auto-Update' --allow-empty")
                    # Phase 2: Direct Vercel Push (The skip-the-line move)
                    output = run_command(f"cd {REPO_PATH} && vercel --prod --yes")
                
                # --- AUTOMATED SYSTEM CHECK ---
                elif "status" in raw_text:
                    output = run_command("uptime && df -h / | tail -1")
                
                # --- DEFAULT BASH ---
                else:
                    output = run_command(task['description'])

                # Save results & update DB
                with open(OUTPUT_FILE, "w") as f: f.write(output)
                supabase.table("tasks").update({"status": "complete"}).eq("id", task_id).execute()
                print(f"✅ TASK {task_id} PROCESSED.")

            time.sleep(1)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    run_worker()
