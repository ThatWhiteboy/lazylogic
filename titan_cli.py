import sys
import time
import os
from supabase import create_client

URL = "https://ntbujdihrfunfxajhzhs.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YnVqZGlocmZ1bmZ4YWpoemhzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODc5NzU5OSwiZXhwIjoyMDg0MzczNTk5fQ.ZrDASOrTH81XgqAyFu7cws9Jdj7lo1BRPrbbO0imsCw"
OUTPUT_FILE = os.path.expanduser("~/lazylogic/titan_output.txt")

def main():
    if len(sys.argv) < 2:
        print("Usage: titan <command>")
        return
    
    cmd = " ".join(sys.argv[1:])
    sb = create_client(URL, KEY)

    # Auto-Bot ID
    try:
        bots = sb.table("bots").select("id").limit(1).execute()
        bot_id = bots.data[0]['id'] if bots.data else None
    except:
        bot_id = None

    # Clear old output
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    # Send Task
    print(f"⚡ Sending: '{cmd}'...", end="", flush=True)
    task = sb.table("tasks").insert({"description": cmd, "status": "pending", "bot_id": bot_id}).execute()
    task_id = task.data[0]['id']
    
    # Wait for result
    print(" Executing...", end="", flush=True)
    for _ in range(30):
        time.sleep(0.5)
        # Check if local file exists (Faster than DB)
        if os.path.exists(OUTPUT_FILE):
            # Double check DB status just to be sure it's THIS task
            check = sb.table("tasks").select("status").eq("id", task_id).execute()
            if check.data and check.data[0]['status'] in ["complete", "failed"]:
                print("\n")
                with open(OUTPUT_FILE, "r") as f:
                    print(f.read())
                return
                
    print("\n⚠️ Timeout.")

if __name__ == "__main__":
    main()
