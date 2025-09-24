import os
import tempfile
import subprocess
from urllib.parse import urlparse

def get_changed_files_from_pr(pr_url: str, branch: str):
    parsed = urlparse(pr_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 4 or parts[-2] != "pull":
        raise ValueError("Invalid PR URL format")
    owner, repo, _, pr_number = parts
    repo_full = f"{owner}/{repo}.git"
    local_path = os.path.join(tempfile.gettempdir(), repo_full)
    print(repo_full, local_path)
    if not os.path.exists(local_path):
        subprocess.run(["git", "clone", f"https://rsa-builder:{os.getenv("GITHUB_TOKEN")}@github.com/{repo_full}", local_path], check=True)
    subprocess.run(["git", "fetch"],cwd=local_path,check=True)
    subprocess.run(["git", "checkout", branch],cwd=local_path,check=True)
    subprocess.run(["git", "pull"],cwd=local_path,check=True)
    base = "origin/master"
    merge_base = subprocess.check_output(["git", "merge-base", base, branch],cwd=local_path,text=True).strip()
    changed_files = subprocess.check_output(["git", "diff", "--name-only", merge_base, branch],cwd=local_path,text=True).splitlines()
    return [local_path + '/' + filename for filename in changed_files]

def push_to_github(pr_url: str, branch: str):
    parsed = urlparse(pr_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 4 or parts[-2] != "pull":
        raise ValueError("Invalid PR URL format")
    owner, repo, _, pr_number = parts
    repo_full = f"{owner}/{repo}.git"
    local_path = os.path.join(tempfile.gettempdir(), repo_full)
    subprocess.run(["git", "add", "."],cwd=local_path,check=True)
    subprocess.run(["git", "commit", "-m", "from agent"],cwd=local_path,check=True)
    subprocess.run(["git", "push", "-u", f"https://rsa-builder:{os.getenv("GITHUB_TOKEN")}@github.com/{repo_full}", branch],cwd=local_path,check=True)

if __name__ == "__main__":
  pr = "https://github.com/rksg/mlisa-ai/pull/135"
  branch = "feature/MLSA-10703-2"
  files = get_changed_files_from_pr(pr, branch)
  print(files)
  with open(files[0], 'a') as file:
    file.write("# test change.\n")
  push_to_github(pr, branch)