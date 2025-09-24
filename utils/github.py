import os
import tempfile
import subprocess
import json
import urllib.request
from urllib.parse import urlparse

def get_branch_from_pr(pr_url: str) -> str:
    parsed = urlparse(pr_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 4 or parts[-2] != "pull":
        raise ValueError("Invalid PR URL format")
    owner, repo, _, pr_number = parts
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN')}"
    req = urllib.request.Request(api_url, headers=headers)
    with urllib.request.urlopen(req) as response:
        pr_data = json.loads(response.read().decode())
        return pr_data["head"]["ref"]

def get_changed_files_from_pr(pr_url: str):
    parsed = urlparse(pr_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 4 or parts[-2] != "pull":
        raise ValueError("Invalid PR URL format")
    owner, repo, _, pr_number = parts
    branch = get_branch_from_pr(pr_url)
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
    return [os.path.join(local_path, filename) for filename in changed_files]

def push_to_github(pr_url: str):
    parsed = urlparse(pr_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 4 or parts[-2] != "pull":
        raise ValueError("Invalid PR URL format")
    owner, repo, _, pr_number = parts
    branch = get_branch_from_pr(pr_url)
    repo_full = f"{owner}/{repo}.git"
    local_path = os.path.join(tempfile.gettempdir(), repo_full)
    subprocess.run(["git", "add", "."],cwd=local_path,check=True)
    subprocess.run(["git", "commit", "-m", "from agent"],cwd=local_path,check=True)
    subprocess.run(["git", "push", "-u", f"https://rsa-builder:{os.getenv("GITHUB_TOKEN")}@github.com/{repo_full}", branch],cwd=local_path,check=True)

if __name__ == "__main__":
  pr = "https://github.com/rksg/mlisa-ai/pull/135"
  files = get_changed_files_from_pr(pr)
  print(files)
  with open(files[0], 'a') as file:
    file.write("# test change.\n")
  push_to_github(pr)
