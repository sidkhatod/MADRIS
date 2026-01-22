import requests
import json
import time
import subprocess
import sys
import os

BASE_URL = "http://127.0.0.1:5000"

def test_flow():
    print("1. Testing Ingestion...")
    # Using a short text that implies a decision to test extraction
    case_study = {
        "text": "At 04:31 AM, the Northridge earthquake struck. The decision was made to shut down gas lines immediately despite lack of confirmation of leaks, fearing fire. This was a critical moment where uncertainty was high.",
        "case_id": "CASE_NORTHRIDGE_001",
        "source_id": "PDF_REPORT_1994"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/ingest/case-study", json=case_study)
        if resp.status_code != 200:
            print(f"Ingest Error {resp.status_code}: {resp.text}")
            return
        data = resp.json()
        print("Ingest Response:", json.dumps(data, indent=2))
        
        if data.get("snapshots_created", 0) == 0:
            print("[FAIL] No snapshots created.")
            return
            
    except Exception as e:
        print(f"Ingest failed exception: {e}")
        return

    print("\n2. Testing Retrieval (Raw Vector Search)...")
    query = {"query": "gas leak fire risk"}
    try:
        resp = requests.post(f"{BASE_URL}/memory/retrieve", json=query)
        data = resp.json()
        print(f"Retrieved {len(data)} items.")
        # print("Retrieve Response:", json.dumps(data, indent=2))
    except Exception as e:
        print(f"Retrieval failed: {e}")

    print("\n3. Testing Reasoning Support (Groq)...")
    narrative = {
        "narrative": "Major tremor felt. Reports of gas smell in sector 7. Should we shut down the main valve?"
    }
    try:
        resp = requests.post(f"{BASE_URL}/reasoning/decision-support", json=narrative)
        data = resp.json()
        print("Reasoning Response:", json.dumps(data, indent=2))
        
        if "support_analysis" in data and isinstance(data["support_analysis"], dict):
             analysis_text = data["support_analysis"].get("analysis", "")
             if len(analysis_text) > 10:
                 print("[PASS] Full flow successful.")
             else:
                 print("[FAIL] Analysis text too short.")
        else:
             print("[FAIL] Reasoning analysis structure incorrect.")
             
    except Exception as e:
        print(f"Reasoning failed: {e}")

if __name__ == "__main__":
    # Start the Flask app as a subprocess
    print("Starting Flask Server...")
    # Assuming run from root of code dir
    env = os.environ.copy()
    server_process = subprocess.Popen([sys.executable, "-m", "api.app"], env=env)
    
    try:
        # Wait for server to boot
        print("Waiting 10s for server to initialize...")
        time.sleep(10) 
        test_flow()
    finally:
        print("Stopping Flask Server...")
        server_process.terminate()
        server_process.wait()
