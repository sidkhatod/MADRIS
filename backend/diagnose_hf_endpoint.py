import os
import requests
import sys
from dotenv import load_dotenv

load_dotenv()

def test_model(model_id, url_pattern):
    token = os.environ.get("HF_API_TOKEN")
    if not token:
        print("[FAIL] HF_API_TOKEN not set")
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    if url_pattern == "models":
        url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
    else:
        url = f"https://router.huggingface.co/hf-inference/pipeline/feature-extraction/{model_id}"
        
    print(f"Testing {model_id} via {url} ...")
    
    try:
        response = requests.post(url, headers=headers, json={"inputs": "Test sentence"})
        
        if response.status_code == 200:
            data = response.json()
            # Check dimension
            dim = 0
            if isinstance(data, list):
                if isinstance(data[0], list):
                    dim = len(data[0])
                else:
                    dim = len(data)
            
            print(f"   [SUCCESS] Status 200. Dimension: {dim}")
            if dim == 384:
                return True
            else:
                print(f"   [WARN] Dimension mismatch (expected 384)")
                return False
        else:
            print(f"   [FAIL] Status {response.status_code}: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Exception: {e}")
        return False

def main():
    models_to_test = [
        "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/all-MiniLM-L12-v2",
        "BAAI/bge-small-en-v1.5",
        "sentence-transformers/paraphrase-MiniLM-L3-v2",
        "intfloat/e5-small-v2"
    ]
    
    print("--- Starting HF Diagnostic ---")
    
    working_config = None
    
    for model in models_to_test:
        # Test /models/ endpoint
        if test_model(model, "models"):
            working_config = (model, "models")
            break
            
        # Test pipeline endpoint
        if test_model(model, "pipeline"):
            working_config = (model, "pipeline")
            break
            
    if working_config:
        print(f"\n[FOUND] Working configuration: Model={working_config[0]}, Endpoint={working_config[1]}")
    else:
        print("\n[FAILED] No working configuration found.")

if __name__ == "__main__":
    main()
