import os
import tempfile
import subprocess
from urllib.parse import urlparse

def get_changed_files_from_pr(pr_url: str):
    parsed = urlparse(pr_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 4 or parts[-2] != "pull":
        raise ValueError("Invalid PR URL format")
    owner, repo, _, pr_number = parts
    repo_full = f"{owner}/{repo}.git"
    local_path = os.path.join(tempfile.gettempdir(), repo_full)
    print(repo_full, local_path)
    if not os.path.exists(local_path):
        subprocess.run(["git", "clone", f"https://{os.getenv("GITHUB_TOKEN")}@github.com/{repo_full}", local_path], check=True)
    subprocess.run(
        ["git", "fetch", "origin", f"pull/{pr_number}/head:pr-{pr_number}"],
        cwd=local_path,
        check=True,
    )
    base = "origin/master"
    merge_base = subprocess.check_output(
        ["git", "merge-base", base, f"pr-{pr_number}"],
        cwd=local_path,
        text=True,
    ).strip()
    # Get list of changed files
    changed_files = subprocess.check_output(
        ["git", "diff", "--name-only", merge_base, f"pr-{pr_number}"],
        cwd=local_path,
        text=True,
    ).splitlines()
    return [local_path + filename for filename in changed_files]

if __name__ == "__main__":
  print(get_changed_files_from_pr("https://github.com/rksg/mlisa-ai/pull/131"))
  print(get_changed_files_from_pr("https://github.com/rksg/mlisa-ai/pull/130"))