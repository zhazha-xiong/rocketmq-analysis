import os
import base64
import requests
from dotenv import load_dotenv

owner, repo = "apache", "rocketmq"
BASE_URL = "https://api.github.com"


def get_headers(token: str) -> dict:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def fetch_repo_info(headers: dict) -> dict:
    """获取仓库基本信息"""
    url = f"{BASE_URL}/repos/{owner}/{repo}"
    print(f"Fetch: {url}")
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def check_file_exists(file_path: str, headers: dict) -> bool:
    """检查文件是否存在"""
    url = f"{BASE_URL}/repos/{owner}/{repo}/contents/{file_path}"
    # print(f"Check: {url}")
    resp = requests.get(url, headers=headers, timeout=10)
    return resp.status_code == 200


def fetch_recent_commits(headers: dict, limit: int = 100) -> list:
    """获取最近的 commits"""
    url = f"{BASE_URL}/repos/{owner}/{repo}/commits"
    params = {"per_page": limit, "page": 1}
    print(f"Fetch: {url} (limit={limit})")
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_recent_prs(headers: dict, state: str = "closed", limit: int = 20) -> list:
    """获取最近的 PR"""
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls"
    params = {
        "state": state,
        "per_page": limit,
        "page": 1,
        "sort": "updated",
        "direction": "desc"
    }
    print(f"Fetch: {url} (limit={limit})")
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_workflow_runs(headers: dict, branch: str = "main", limit: int = 50) -> list:
    """获取 CI 运行历史"""
    url = f"{BASE_URL}/repos/{owner}/{repo}/actions/runs"
    params = {"branch": branch, "per_page": limit, "page": 1}
    print(f"Fetch: {url} (limit={limit})")
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("workflow_runs", [])


def fetch_file_content(file_path: str, headers: dict) -> str | None:
    """获取文件内容（文本）"""
    url = f"{BASE_URL}/repos/{owner}/{repo}/contents/{file_path}"
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code == 200:
        content_b64 = resp.json().get("content", "")
        if content_b64:
            return base64.b64decode(content_b64).decode("utf-8", errors="ignore")
    return None


def main() -> None:
    # 加载环境变量
    load_dotenv()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("请在scripts/module_c/.env填写GITHUB_TOKEN")

    headers = get_headers(token)
    
    # 1. Repo Info
    try:
        info = fetch_repo_info(headers)
        print(f"[INFO] Repo: {info['full_name']}, Stars: {info['stargazers_count']}")
    except Exception as e:
        print(f"[ERROR] Fetch repo info failed: {e}")

    # 2. Check Files
    files_to_check = ["README.md", "LICENSE", "pom.xml"]
    for f in files_to_check:
        exists = check_file_exists(f, headers)
        print(f"[INFO] File '{f}' exists: {exists}")

    # 3. Recent Commits
    try:
        commits = fetch_recent_commits(headers, limit=5)
        if commits:
             print(f"[INFO] Fetched {len(commits)} commits. Latest: {commits[0]['commit']['message'].splitlines()[0]}")
    except Exception as e:
        print(f"[ERROR] Fetch commits failed: {e}")


if __name__ == "__main__":
    main()
