#!/bin/bash

# TITAN PROTOCOL: FINALIZATION
# User: thatwhiteboy
# System: Nick PC (Kali)

echo "🚀 Initiating Total Automation Sequence..."

# 1. Install System Monitor Dependencies
echo "📦 Installing psutil for Heartbeat Monitor..."
/home/thatwhiteboy/lazylogic/venv/bin/pip install psutil

# 2. Deploy Doomsday Backup Script
echo "🛡️ Creating Doomsday Backup Protocol..."
cat << 'EOF' > /home/thatwhiteboy/lazylogic/titan_backup.py
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
EOF

# 3. Upgrade Master Orchestrator (Heartbeat + Health Check)
echo "❤️ Upgrading Orchestrator with Health Monitoring..."
cat << 'EOF' > /home/thatwhiteboy/lazylogic/master_orchestrator.py
import os
import time
import requests
import sys
import psutil
from supabase import create_client, Client
from dotenv import load_dotenv

# Unbuffered output for Journalctl
sys.stdout.reconfigure(line_buffering=True)
load_dotenv("/home/thatwhiteboy/lazylogic/.env")

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
WEBHOOK = os.environ.get("N8N_WEBHOOK_URL")

supabase: Client = create_client(URL, KEY)

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [TITAN] {msg}")

def check_health():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    if cpu > 90 or ram > 90 or disk > 90:
        log(f"CRITICAL ALERT: CPU {cpu}% | RAM {ram}% | DISK {disk}%")
        try:
            payload = {
                "id": "SYSTEM_ALERT",
                "description": f"CRITICAL SYSTEM HEALTH: CPU {cpu}% | RAM {ram}% | DISK {disk}%",
                "bot": "Sentinel"
            }
            requests.post(WEBHOOK, json=payload, timeout=5)
        except:
            pass
    return cpu, ram, disk

def process_tasks():
    try:
        # 1. Pulse Check
        check_health()
        
        # 2. Check for Orders
        response = supabase.table("tasks").select("*").eq("status", "pending").limit(1).execute()
        if response.data:
            task = response.data[0]
            log(f"Processing Task: {task['description']} (Bot: {task['bot_id']})")
            
            # Lock & Load
            supabase.table("tasks").update({"status": "executing"}).eq("id", task['id']).execute()
            
            # Dispatch
            payload = {"id": task['id'], "description": task['description'], "bot": task['bot_id']}
            requests.post(WEBHOOK, json=payload, timeout=5)
            log(f"Success: Handoff to n8n complete.")

    except Exception as e:
        log(f"Loop Error: {e}")

if __name__ == "__main__":
    log("System Online. Heartbeat Monitor Active.")
    while True:
        process_tasks()
        time.sleep(5)
EOF

# 4. Inject Cron Jobs (Backups @ 3AM, Deploy @ Hourly)
echo "⏰ Injecting Automation Schedules (Cron)..."
(crontab -l 2>/dev/null; echo "0 3 * * * /home/thatwhiteboy/lazylogic/venv/bin/python /home/thatwhiteboy/lazylogic/titan_backup.py >> /home/thatwhiteboy/lazylogic/backup.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 * * * * /home/thatwhiteboy/lazylogic/deploy_drone.sh >> /home/thatwhiteboy/lazylogic/deploy.log 2>&1") | crontab -

# 5. Restart Engine
echo "🔄 Restarting Titan Engine..."
sudo systemctl restart titan-engine

echo "✅ TITAN PROTOCOL: FULLY OPERATIONAL."
