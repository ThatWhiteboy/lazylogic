import time
import subprocess
import os
from supabase import create_client

# --- CONFIG ---
URL = "https://ntbujdihrfunfxajhzhs.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YnVqZGlocmZ1bmZ4YWpoemhzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODc5NzU5OSwiZXhwIjoyMDg0MzczNTk5fQ.ZrDASOrTH81XgqAyFu7cws9Jdj7lo1BRPrbbO0imsCw"
REPO_PATH = os.path.expanduser("~/lazylogic")
OUTPUT_FILE = os.path.expanduser("~/lazylogic/titan_output.txt")

def run_worker():
    print("🦾 TITAN NETLIFY ENGINE: Online...")
    supabase = create_client(URL, KEY)

    while True:
        try:
            response = supabase.table("tasks").select("*").eq("status", "pending").execute()
            for task in response.data:
                task_id = task['id']
                supabase.table("tasks").update({"status": "processing"}).eq("id", task_id).execute()
                
                # THE NETLIFY PUSH
                # --prod: Sends it live
                # --dir .: Tells Netlify to use the current folder as the website root
                print(f"🚀 DEPLOYING TO NETLIFY (PROD)...")
                res = subprocess.run(f"cd {REPO_PATH} && netlify deploy --prod --dir .", shell=True, capture_output=True, text=True)
                output = res.stdout if res.returncode == 0 else f"❌ ERROR:\n{res.stderr}"

                with open(OUTPUT_FILE, "w") as f: f.write(output)
                supabase.table("tasks").update({"status": "complete"}).eq("id", task_id).execute()
                print(f"✅ DEPLOY COMPLETE.")
            time.sleep(1)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    run_worker()
