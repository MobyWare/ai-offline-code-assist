import requests
import json
import csv
import time
import argparse
import sys

def pre_warm_model(url, model_name):
    """Triggers the model load without generating tokens."""
    print(f"🔥 Pre-warming {model_name}... (This may take 10-30s)")
    try:
        # Sending model name with no prompt triggers a load in Ollama
        # keep_alive: -1 ensures it stays in VRAM for all subsequent tests
        payload = {"model": model_name, "keep_alive": -1}
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        print("✅ Model loaded and ready.\n")
    except Exception as e:
        print(f"⚠️ Pre-warm failed: {e}. Benchmarks might be skewed by load times.\n")

def run_benchmark():
    parser = argparse.ArgumentParser(description="Ollama Coding Assistant Benchmarker")
    parser.add_argument("--host", default="http://localhost", help="The host URL")
    parser.add_argument("--port", default="11434", help="The port number")
    parser.add_argument("--path", default="/api/generate", help="The API path")
    parser.add_argument("--file", default="./prompts/general.json", help="Test JSON file")
    parser.add_argument("--output", default="./scratch/benchmark_results.csv", help="CSV output")
    parser.add_argument("--no-warm", action="store_true", help="Skip the pre-warm step")
    parser.add_argument("--timeout", default=120, help="Request timeout in seconds (120 default)")
    
    args = parser.parse_args()
    full_url = f"{args.host.rstrip('/')}:{args.port}{args.path}"
    
    # Load Test Data
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            test_cases = json.load(f)
    except FileNotFoundError:
        print(f"Error: {args.file} not found.")
        sys.exit(1)

    # Step 1: Pre-warm the specific model used in the first test case
    if not args.no_warm and test_cases:
        target_model = test_cases[0]["payload"].get("model")
        pre_warm_model(full_url, target_model)

    results = []
    
    # Step 2: Run Suite
    for case in test_cases:
        name = case.get("name", "Unnamed Task")
        print(f"🚀 Running: {name}...", end=" ", flush=True)
        
        try:
            response = requests.post(full_url, json=case["payload"], timeout=args.timeout)
            response.raise_for_status()
            data = response.json()

            eval_dur = data.get("eval_duration", 1) / 1e9
            tps = data.get("eval_count", 0) / eval_dur if eval_dur > 0 else 0

            results.append({
                "Task": name,
                "Status": "Success",
                "Tokens/Sec": round(tps, 2),
                "Latency (s)": round(data.get("total_duration", 0) / 1e9, 2),
                "Output Length": data.get("eval_count", 0)
            })
            print(f"DONE ({round(tps, 2)} tok/s)")

        except Exception as e:
            print(f"FAILED")
            results.append({"Task": name, "Status": f"Error: {str(e)}"})

    # Step 3: Save Results
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\n✅ Results saved to {args.output}")

if __name__ == "__main__":
    run_benchmark()