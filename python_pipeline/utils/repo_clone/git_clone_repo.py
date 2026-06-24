from pathlib import Path
from urllib.parse import urlparse
import subprocess
from python_pipeline.utils.repo_clone.delete_repo import delete_repo

def clone_repo(repo_url: str) -> str:
    try:
        parsed = urlparse(repo_url)

        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub repository URL")

        owner = path_parts[-2]
        repo = path_parts[-1].replace(".git", "")

        target_dir = Path("python_pipeline/input_code") / f"{owner}_{repo}"

        target_dir.parent.mkdir(parents=True, exist_ok=True)

        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                repo_url,
                str(target_dir),
            ],
            check=True,
        )

        return str(target_dir)
    except Exception as e:
        delete_repo(target_dir)
        raise ValueError(f"Error occured while cloning \n {e}")

if __name__ == "__main__":
    target_dir = clone_repo("https://github.com/programiz/Calculator")
    print(target_dir)