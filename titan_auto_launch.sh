#!/bin/bash
# TITAN CLOUD | FINAL AUTOMATION
# STATUS: KEYS DETECTED via CHAT

# 1. HARDCODED CREDENTIALS (AUTO-FILLED)
SUPABASE_URL="https://ntbujdihrfunfxajhzhs.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YnVqZGlocmZ1bmZ4YWpoemhzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODc5NzU5OSwiZXhwIjoyMDg0MzczNTk5fQ.ZrDASOrTH81XgqAyFu7cws9Jdj7lo1BRPrbbO0imsCw"
N8N_WEBHOOK="http://localhost:5678/webhook/titan-dispatch"

echo "=========================================="
echo "   TITAN CLOUD | LAUNCH SEQUENCE          "
echo "=========================================="

# 2. SYSTEM PREP
echo "🔧 Configuring Environment..."
sudo apt update -qq
sudo apt install -y python3-venv python3-pip
mkdir -p ~/lazylogic/backups
cd ~/lazylogic

# Write credentials file
echo "SUPABASE_URL=\"$SUPABASE_URL\"" > .env
echo "SUPABASE_KEY=\"$SUPABASE_KEY\"" >> .env
echo "N8N_WEBHOOK_URL=\"$N8N_WEBHOOK\"" >> .env

# Setup Python
python3 -m venv venv
./venv/bin/pip install supabase requests python-dotenv psutil

# 3. DEPLOY INTELLIGENCE (ORCHESTRATOR)
echo "🧠 Deploying Master Orchestrator..."
cat << 'PY_EOF' > master_orchestrator.py
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
PY_EOF

# 4. DEPLOY PERSISTENCE (SYSTEMD)
echo "🔌 Installing Background Service..."
cat << SERVICE_EOF | sudo tee /etc/systemd/system/titan-engine.service
[Unit]
Description=Titan Cloud Engine
After=network.target

[Service]
Type=simple
User=thatwhiteboy
WorkingDirectory=/home/thatwhiteboy/lazylogic
ExecStart=/home/thatwhiteboy/lazylogic/venv/bin/python /home/thatwhiteboy/lazylogic/master_orchestrator.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# 5. ACTIVATE
sudo systemctl daemon-reload
sudo systemctl enable titan-engine
sudo systemctl restart titan-engine

echo ""
echo "✅ DEPLOYMENT COMPLETE."
echo "System is now running. Monitoring logs below (Press Ctrl+C to exit logs):"
echo "------------------------------------------------------------------"
sudo journalctl -u titan-engine -f
