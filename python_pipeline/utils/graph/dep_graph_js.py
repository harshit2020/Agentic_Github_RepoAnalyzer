import subprocess
import json
import os


def dep_graph_js():
    try:
        js_dir = os.path.abspath("js_support")

        result = subprocess.run(
            ["node", "dep_graph.js"],
            cwd=js_dir, 
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print("JS Dependency graph error!!")

if __name__ == "__main__":
    dep_graph_js()