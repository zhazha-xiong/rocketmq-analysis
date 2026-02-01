import os
import json

from module_utils import (
    github_get_json,
    github_headers,
    load_github_token,
    repo_root_from,
    write_json,
)


def main() -> None:
    token = load_github_token(missing_hint="请在scripts/.env填写GITHUB_TOKEN", caller_file=__file__)

    owner, repo = "apache", "rocketmq"
    
    headers = github_headers(token)
    
    repo_root = repo_root_from(__file__)
    out_dir = os.path.join(repo_root, "data", "module_c")

    print("===开始采集数据===")

    # 1. Repo Info
    url_repo = f"https://api.github.com/repos/{owner}/{repo}"
    print(f"Fetch: {url_repo}")
    repo_info = github_get_json(url_repo, headers=headers, timeout=30)
    write_json(os.path.join(out_dir, "repo_info.json"), repo_info)

    # 2. Recent Commits
    url_commits = f"https://api.github.com/repos/{owner}/{repo}/commits"
    params_commits = {"per_page": 100, "page": 1}
    print(f"Fetch: {url_commits}")
    commits = github_get_json(url_commits, headers=headers, params=params_commits, timeout=30)
    write_json(os.path.join(out_dir, "commits.json"), commits)

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
    prs = github_get_json(url_prs, headers=headers, params=params_prs, timeout=30)
    write_json(os.path.join(out_dir, "pull_requests.json"), prs)

    # 4. Workflow Runs
    url_runs = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    params_runs = {"branch": "main", "per_page": 50, "page": 1}
    print(f"Fetch: {url_runs}")
    runs_resp = github_get_json(url_runs, headers=headers, params=params_runs, timeout=30)
    runs = (runs_resp or {}).get("workflow_runs", [])
    write_json(os.path.join(out_dir, "workflow_runs.json"), runs)
    
    # 5. Releases
    url_releases = f"https://api.github.com/repos/{owner}/{repo}/releases"
    params_releases = {"per_page": 20, "page": 1}
    print(f"Fetch: {url_releases}")
    releases = github_get_json(url_releases, headers=headers, params=params_releases, timeout=30)
    write_json(os.path.join(out_dir, "releases.json"), releases)

    # 6. Check Critical Files
    files_to_check = [
        "LICENSE", 
        "README.md", 
        "CONTRIBUTING.md", 
        "CODE_OF_CONDUCT.md", 
        "pom.xml", 
        ".editorconfig",
        ".github/workflows"
    ]
    file_status = {}
    print("Checking files...")
    for fpath in files_to_check:
        url_file = f"https://api.github.com/repos/{owner}/{repo}/contents/{fpath}"
        try:
            github_get_json(url_file, headers=headers, timeout=10)
            file_status[fpath] = True
        except Exception:
            file_status[fpath] = False
        print(f"  - {fpath}: {file_status[fpath]}")
        
        if fpath == "pom.xml" and file_status[fpath]:
            try:
                pom_obj = github_get_json(url_file, headers=headers, timeout=10)
                content_b64 = (pom_obj or {}).get("content", "")
                import base64
                if content_b64:
                    content_str = base64.b64decode(content_b64).decode("utf-8", errors="ignore")
                    has_checkstyle = "maven-checkstyle-plugin" in content_str
                    has_spotless = "spotless-maven-plugin" in content_str
                    file_status["pom_style_check"] = has_checkstyle or has_spotless
                    print(f"    > Checkstyle/Spotless configured: {file_status['pom_style_check']}")
            except Exception as e:
                print(f"    > Failed to parse pom.xml: {e}")
                file_status["pom_style_check"] = False

    write_json(os.path.join(out_dir, "files_structure.json"), file_status)

    print("[OK] 数据采集完成")


if __name__ == "__main__":
    main()
