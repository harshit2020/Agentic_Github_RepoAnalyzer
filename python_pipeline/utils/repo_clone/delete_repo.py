from pathlib import Path
import shutil


def delete_repo(repo_path: str) -> None:
    path = Path(repo_path).resolve()
    base = Path("python_pipeline/input_code").resolve()

    if not str(path).startswith(str(base)):
        raise ValueError("Refusing to delete outside input_code directory")

    if path.exists():
        shutil.rmtree(path)
    print(f"repo deleted at path = {repo_path}")

if __name__ == "__main__":
    delete_repo("python_pipeline/input_code/programiz_Calculator")