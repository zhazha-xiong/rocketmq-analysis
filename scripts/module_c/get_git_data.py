import os
import json
import requests
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("请在scripts/module_c/.env填写GITHUB_TOKEN")

    owner, repo = "apache", "rocketmq"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    out_dir = os.path.join(repo_root, "data", "module_c")
    os.makedirs(out_dir, exist_ok=True)

    print("===开始采集数据===")

    # 1. Repo Info
    url_repo = f"https://api.github.com/repos/{owner}/{repo}"
    print(f"Fetch: {url_repo}")
    r_repo = requests.get(url_repo, headers=headers, timeout=30)
    r_repo.raise_for_status()
    repo_info = r_repo.json()
    
    with open(os.path.join(out_dir, "repo_info.json"), "w", encoding="utf-8") as f:
        json.dump(repo_info, f, ensure_ascii=False, indent=2)

    # 2. Recent Commits
    url_commits = f"https://api.github.com/repos/{owner}/{repo}/commits"
    params_commits = {"per_page": 100, "page": 1}
    print(f"Fetch: {url_commits}")
    r_commits = requests.get(url_commits, headers=headers, params=params_commits, timeout=30)
    r_commits.raise_for_status()
    commits = r_commits.json()

    with open(os.path.join(out_dir, "commits.json"), "w", encoding="utf-8") as f:
        json.dump(commits, f, ensure_ascii=False, indent=2)

    # 3. Pull Requests
    url_prs = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    params_prs = {
        "state": "closed",
        "per_page": 20,
        "page": 1,
        "sort": "updated",
        "direction": "desc"
    }
    print(f"Fetch: {url_prs}")
    r_prs = requests.get(url_prs, headers=headers, params=params_prs, timeout=30)
    r_prs.raise_for_status()
    prs = r_prs.json()

    with open(os.path.join(out_dir, "pull_requests.json"), "w", encoding="utf-8") as f:
        json.dump(prs, f, ensure_ascii=False, indent=2)

    # 4. Workflow Runs
    url_runs = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    params_runs = {"branch": "main", "per_page": 50, "page": 1}
    print(f"Fetch: {url_runs}")
    r_runs = requests.get(url_runs, headers=headers, params=params_runs, timeout=30)
    r_runs.raise_for_status()
    runs = r_runs.json().get("workflow_runs", [])

    with open(os.path.join(out_dir, "workflow_runs.json"), "w", encoding="utf-8") as f:
        json.dump(runs, f, ensure_ascii=False, indent=2)
    
    # 5. Releases
    url_releases = f"https://api.github.com/repos/{owner}/{repo}/releases"
    params_releases = {"per_page": 20, "page": 1}
    print(f"Fetch: {url_releases}")
    r_releases = requests.get(url_releases, headers=headers, params=params_releases, timeout=30)
    r_releases.raise_for_status()
    releases = r_releases.json()

    with open(os.path.join(out_dir, "releases.json"), "w", encoding="utf-8") as f:
        json.dump(releases, f, ensure_ascii=False, indent=2)

    print("[OK] 数据采集完成")


if __name__ == "__main__":
    main()
