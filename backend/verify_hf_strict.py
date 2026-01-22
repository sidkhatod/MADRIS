import os
import requests
import sys
from dotenv import load_dotenv

# Load env variables from .env file
load_dotenv()

def verify_hf_strict():
    token = os.environ.get("HF_API_TOKEN")
    if not token:
        print("[FAIL] HF_API_TOKEN not set.")
        return

    print(f"[OK] Token found: {token[:4]}...")
    
    url = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en-v1.5"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"inputs": "Antigravity verification"}
    
    print(f"Post to: {url}")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Strict checks
        if not isinstance(data, list):
            print(f"[FAIL] Response is not a list: {type(data)}")
            return
            
        embedding = data
        if isinstance(data[0], list):
             embedding = data[0]
             
        print(f"[OK] Received embedding of length: {len(embedding)}")
        
        if len(embedding) == 384:
            print("[PASS] Dimension is 384.")
        else:
            print(f"[FAIL] Dimension mismatch: {len(embedding)}")

    except Exception as e:
        print(f"[FAIL] Request failed: {e}")

if __name__ == "__main__":
    verify_hf_strict()
