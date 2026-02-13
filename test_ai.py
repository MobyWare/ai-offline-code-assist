import requests
import json
import csv
import time

# Configuration
API_URL = "http://localhost:11435/api/generate"  # Change to your k8s service DNS in production
MODEL_NAME = "deepseek-coder:6.7b"
OUTPUT_FILE = "./scratch/ollama_benchmark_results.csv"

# Define representative coding tasks
TEST_CASES = [
    {
        "name": "Function Generation",
        "prompt": "Write a Python function to calculate the rolling average of a list of numbers given a window size.",
        "suffix": ""
    },
    {
        "name": "Fill-In-The-Middle (FIM)",
        "prompt": "def find_max(numbers):\n    max_val = numbers[0]\n    for num in numbers:",
        "suffix": "\n    return max_val"
    },
    {
        "name": "Bug Fixing",
        "prompt": "Fix the bug in this code:\ndef add_to_list(val, my_list=[]):\n    my_list.append(val)\n    return my_list",
        "suffix": ""
    },
    {
        "name": "Unit Test Generation",
        "prompt": "Create a pytest test suite for a function called `validate_email(email)`.",
        "suffix": ""
    }
]

def run_benchmark():
    results = []

    print(f"Starting benchmark for model: {MODEL_NAME}...")
    
    for case in TEST_CASES:
        payload = {
            "model": MODEL_NAME,
            "prompt": case["prompt"],
            "suffix": case["suffix"],
            "stream": False,
            "options": {"temperature": 0} # Deterministic for benchmarking
        }

        try:
            start_wall_time = time.time()
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            end_wall_time = time.time()

            # Ollama provides durations in nanoseconds
            total_duration_s = data.get("total_duration", 0) / 1e9
            prompt_eval_duration_s = data.get("prompt_eval_duration", 0) / 1e9
            eval_duration_s = data.get("eval_duration", 0) / 1e9
            
            # Metrics
            input_tokens = data.get("prompt_eval_count", 0)
            output_tokens = data.get("eval_count", 0)
            # Generation Speed (TPS)
            tps = output_tokens / eval_duration_s if eval_duration_s > 0 else 0

            results.append({
                "Task": case["name"],
                "Status": "Success",
                "Input Tokens": input_tokens,
                "Output Tokens": output_tokens,
                "Total Latency (s)": round(total_duration_s, 2),
                "Prompt Eval (s)": round(prompt_eval_duration_s, 2),
                "Tokens/Sec": round(tps, 2)
            })
            print(f"✅ Finished: {case['name']} ({round(tps, 2)} tok/s)")

        except Exception as e:
            print(f"❌ Failed: {case['name']} - {str(e)}")
            results.append({"Task": case["name"], "Status": f"Error: {str(e)}"})

    # Save to CSV
    keys = results[0].keys()
    with open(OUTPUT_FILE, 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)
    
    print(f"\nBenchmark complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_benchmark()
