import time, subprocess, os
from supabase import create_client

URL = "https://ntbujdihrfunfxajhzhs.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YnVqZGlocmZ1bmZ4YWpoemhzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODc5NzU5OSwiZXhwIjoyMDg0MzczNTk5fQ.ZrDASOrTH81XgqAyFu7cws9Jdj7lo1BRPrbbO0imsCw"
REPO_PATH = os.path.expanduser("~/lazylogic")

def run_worker():
    print("🦾 TITAN GITHUB-PIPE: Online...")
    supabase = create_client(URL, KEY)
    while True:
        try:
            res = supabase.table("tasks").select("*").eq("status", "pending").execute()
            for task in res.data:
                cmd = task['description'].lower()
                supabase.table("tasks").update({"status": "processing"}).eq("id", task['id']).execute()
                
                # THE FIX: Push to GitHub instead of fighting the Netlify CLI
                if "deploy" in cmd or "report" in cmd:
                    final_cmd = f"cd {REPO_PATH} && git add . && git commit -m 'Titan Auto-Sync' --allow-empty && git push origin main --force"
                else:
                    final_cmd = task['description']

                process = subprocess.run(final_cmd, shell=True, capture_output=True, text=True)
                status = "complete" if process.returncode == 0 else "failed"
                supabase.table("tasks").update({"status": status}).eq("id", task['id']).execute()
            time.sleep(1)
        except: time.sleep(5)

if __name__ == "__main__":
    run_worker()
