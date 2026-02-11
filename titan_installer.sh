#!/bin/bash
# TITAN CLOUD AUTO-INSTALLER
# Status: WAITING FOR KEYS

echo "=========================================="
echo "   TITAN CLOUD | SYSTEM PREPARATION       "
echo "=========================================="

# 1. Install Software (While Supabase Wakes Up)
echo "⏳ Installing Python & System Tools..."
sudo apt update -qq
sudo apt install -y python3-venv python3-pip
mkdir -p ~/lazylogic/backups
cd ~/lazylogic
python3 -m venv venv
./venv/bin/pip install supabase requests python-dotenv psutil

# 2. Wait for User Input
echo ""
echo "------------------------------------------"
echo "🚨 STOP: Your Supabase Project is restarting."
echo "Check the dashboard: https://supabase.com/dashboard/project/ntbujdihrfunfxajhzhs"
echo "Once it is GREEN (Online), paste the keys below."
echo "------------------------------------------"
echo ""
echo "Paste Supabase URL (https://...):"
read -r SUPABASE_URL
echo "Paste Service Role Key (starts with ey...):"
read -r SUPABASE_KEY

# 3. Create Credentials File
cat << EOF > .env
SUPABASE_URL="$SUPABASE_URL"
SUPABASE_KEY="$SUPABASE_KEY"
N8N_WEBHOOK_URL="http://localhost:5678/webhook/titan-dispatch"
EOF

# 4. Create The Master Brain
cat << 'EOF' > master_orchestrator.py
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
    print("[TITAN] Connected to Supabase successfully.")
except:
    print("[CRITICAL] Database Connection Failed. Is the project paused?")
    sys.exit(1)

def process_tasks():
    try:
        response = supabase.table("tasks").select("*").eq("status", "pending").limit(1).execute()
        if response.data:
            task = response.data[0]
            print(f"[TITAN] Processing: {task['description']}")
            supabase.table("tasks").update({"status": "executing"}).eq("id", task['id']).execute()
            requests.post(WEBHOOK, json={"id": task['id'], "text": task['description']})
    except Exception as e:
        print(f"[TITAN] Error: {e}")

if __name__ == "__main__":
    print("[TITAN] System Online.")
    while True:
        process_tasks()
        time.sleep(5)
EOF

# 5. Launch
echo "🚀 Starting Titan Engine..."
cat << EOF | sudo tee /etc/systemd/system/titan-engine.service
[Unit]
Description=Titan Cloud Engine
After=network.target

[Service]
Type=simple
User=thatwhiteboy
WorkingDirectory=/home/thatwhiteboy/lazylogic
ExecStart=/home/thatwhiteboy/lazylogic/venv/bin/python /home/thatwhiteboy/lazylogic/master_orchestrator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable titan-engine
sudo systemctl restart titan-engine

echo "✅ DONE. Logs streaming below..."
sudo journalctl -u titan-engine -f
