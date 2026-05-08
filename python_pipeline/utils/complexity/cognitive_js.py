import subprocess
import json
import os


def cognitive_js():
    try:
        js_dir = os.path.abspath("js_support")

        result = subprocess.run(
            ["node", "cognitive_complexity.js"],
            cwd=js_dir, 
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print("Cognitive complexity computation error!!")

if __name__ == "__main__":
    cognitive_js()