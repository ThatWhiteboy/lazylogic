import os, time, requests, sys, psutil
from supabase import create_client
from dotenv import load_dotenv

sys.stdout.reconfigure(line_buffering=True)
load_dotenv("/home/thatwhiteboy/lazylogic/.env")

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
WEBHOOK = os.environ.get("N8N_WEBHOOK_URL")

try:
    supabase = create_client(URL, KEY)
    print("[TITAN] Database Connected Successfully.")
except Exception as e:
    print(f"[CRITICAL] Connection Failed: {e}")
    sys.exit(1)

def process_tasks():
    try:
        # Check Health
        cpu = psutil.cpu_percent(interval=1)
        if cpu > 90: print(f"[TITAN] ALERT: High CPU {cpu}%")

        # Check Tasks
        response = supabase.table("tasks").select("*").eq("status", "pending").limit(1).execute()
        if response.data:
            task = response.data[0]
            print(f"[TITAN] Processing: {task['description']}")
            supabase.table("tasks").update({"status": "executing"}).eq("id", task['id']).execute()
            
            # Dispatch
            try:
                requests.post(WEBHOOK, json={"id": task['id'], "text": task['description']}, timeout=5)
                print("[TITAN] Handed off to n8n.")
            except:
                print("[TITAN] n8n Unreachable. Retrying...")
    except Exception as e:
        print(f"[TITAN] Error: {e}")

if __name__ == "__main__":
    print("[TITAN] System Online. Listening for tasks...")
    while True:
        process_tasks()
        time.sleep(5)
