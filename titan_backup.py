import os
import json
import time
from supabase import create_client
from dotenv import load_dotenv

load_dotenv("/home/thatwhiteboy/lazylogic/.env")
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

BACKUP_DIR = "/home/thatwhiteboy/lazylogic/backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_table(table_name):
    try:
        data = supabase.table(table_name).select("*").execute().data
        filename = f"{BACKUP_DIR}/{table_name}_{time.strftime('%Y%m%d')}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"[BACKUP] Saved {table_name} to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to backup {table_name}: {e}")

if __name__ == "__main__":
    print(f"[TITAN BACKUP] Starting Sequence: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    backup_table("tasks")
    backup_table("bots")
    backup_table("audit_logs")
