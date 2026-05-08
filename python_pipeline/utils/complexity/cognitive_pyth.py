from pathlib import Path
from complexipy import file_complexity
import json

def analyze_project(root_path: str):
    project = Path(root_path)
    results = []

    for py_file in project.rglob("*.py"):
        if "venv" in str(py_file) or ".venv" in str(py_file):
            continue

        try:
            result = file_complexity(str(py_file))
            results.append({
                'file': str(py_file),
                'complexity': result.complexity,
                'functions': [
                    {
                        'name': f.name,
                        'complexity': f.complexity,
                        'line_start': f.line_start,
                        'line_end': f.line_end
                    }
                    for f in result.functions
                ]
            })
        except Exception as e:
            print(f"Error analyzing {py_file}: {e}")

    # Sort by complexity
    results.sort(key=lambda x: x['complexity'], reverse=True)

    # Save report
    with open("complexity-report.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    total_files = len(results)
    total_complexity = sum(r['complexity'] for r in results)
    avg_complexity = total_complexity / total_files if total_files else 0

    print(f"Analyzed {total_files} files")
    print(f"Total complexity: {total_complexity}")
    print(f"Average complexity: {avg_complexity:.2f}")

    # Top 10 most complex files
    print("\nTop 10 most complex files:")
    for r in results[:10]:
        print(f"  {r['file']}: {r['complexity']}")

if __name__ == "__main__":
    analyze_project("./input_code")