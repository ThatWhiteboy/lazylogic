import requests
import json
import sys

# --- YOUR KEYS ---
N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjOTZkMTAxMC03YjExLTRmNWMtYTk3OS00Y2I3YjI0Nzc5NWQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiMjM0OTI4MjYtYTM5YS00MjkxLTkwMTgtMWI0MjZhOTAzYmIxIiwiaWF0IjoxNzcwNzAyMDIwLCJleHAiOjE3NzMyODgwMDB9.4Q1-PAKaottHxoxaJcbB3iB88amc3AOOLX-zDjLMMmg"
SUPA_URL = "https://ntbujdihrfunfxajhzhs.supabase.co"
SUPA_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YnVqZGlocmZ1bmZ4YWpoemhzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODc5NzU5OSwiZXhwIjoyMDg0MzczNTk5fQ.ZrDASOrTH81XgqAyFu7cws9Jdj7lo1BRPrbbO0imsCw"

API_URL = "http://localhost:5678/api/v1"
HEADERS = {"X-N8N-API-KEY": N8N_KEY}

def run():
    print("🚀 RE-ATTEMPTING CONFIGURATION...")

    # 1. CREATE CREDENTIALS (NEW FORMAT)
    cred_payload = {
        "name": "Titan Supabase V2",
        "type": "supabaseApi",
        "data": {
            "host": SUPA_URL,          # FIXED: Was 'url'
            "serviceRole": SUPA_KEY    # FIXED: Was 'serviceRoleSecret'
        }
    }
    
    # Check existing
    creds = requests.get(f"{API_URL}/credentials", headers=HEADERS).json()
    existing_id = None
    for c in creds.get('data', []):
        if c['name'] == "Titan Supabase V2":
            existing_id = c['id']
            break
            
    if existing_id:
        print(f"✅ Credentials found (ID: {existing_id}). Updating...")
        requests.put(f"{API_URL}/credentials/{existing_id}", headers=HEADERS, json=cred_payload)
        final_cred_id = existing_id
    else:
        print("🛠 Creating NEW Credentials...")
        resp = requests.post(f"{API_URL}/credentials", headers=HEADERS, json=cred_payload)
        if resp.status_code != 200:
            print(f"❌ Credential Failed Again: {resp.text}")
            sys.exit(1)
        final_cred_id = resp.json()['data']['id']
        print(f"✅ Credentials Created (ID: {final_cred_id})")

    # 2. CREATE WORKFLOW
    workflow_json = {
        "name": "Titan Master Workflow V2",
        "nodes": [
            {
                "parameters": { "path": "titan-dispatch", "responseMode": "lastNode", "options": {} },
                "name": "Webhook", "type": "n8n-nodes-base.webhook", "typeVersion": 1, "position": [460, 300], "webhookId": "titan-dispatch"
            },
            {
                "parameters": { "operation": "getAll", "tableId": "tasks", "limit": 1 },
                "name": "Supabase", "type": "n8n-nodes-base.supabase", "typeVersion": 1, "position": [680, 300],
                "credentials": { "supabaseApi": { "id": final_cred_id, "name": "Titan Supabase V2" } }
            }
        ],
        "connections": { "Webhook": { "main": [[{ "node": "Supabase", "type": "main", "index": 0 }]] } }
    }

    print("🧠 Uploading Master Workflow...")
    resp = requests.post(f"{API_URL}/workflows", headers=HEADERS, json=workflow_json)
    
    if resp.status_code == 200:
        wf_id = resp.json()['data']['id']
        print(f"✅ WORKFLOW CREATED (ID: {wf_id})")
        requests.post(f"{API_URL}/workflows/{wf_id}/activate", headers=HEADERS)
        print("✅ WORKFLOW ACTIVATED.")
    else:
        print(f"⚠️ Workflow upload issue: {resp.text}")

if __name__ == "__main__":
    run()
