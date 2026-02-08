import os
import csv
import sys
from pathlib import Path
from datetime import datetime, timezone

# 增加 scripts 目录到环境变量
sys.path.append(str(Path(__file__).parent.parent))
from config_utils import load_config
from module_utils import github_get_json, github_headers, load_github_token, repo_root_from

CONFIG = load_config()

def main() -> None:
    """运行 Module B 的数据抓取流程"""
    token = load_github_token(missing_hint="请在scripts/.env填写GITHUB_TOKEN", caller_file=__file__)

    project = CONFIG.get('project', {})
    owner = project.get('repo_owner', 'apache')
    repo = project.get('repo_name', 'rocketmq')
    
    # 获取配置中的其实时间
    since = CONFIG.get('module_b', {}).get('since_date', "2013-01-01") + "T00:00:00Z"
    if len(since) > 20: # 简单检查用户是否提供了完整时间
         # If config has T... keep it, else append
         pass 

    until = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    headers = github_headers(token)

    page = 1
    total = 0

    data_dir = Path(CONFIG['paths']['data']) / "module_b"
    out_path = data_dir / "commits.csv"
    os.makedirs(data_dir, exist_ok=True)

    print(f"===开始采集数据 [{owner}/{repo}]===")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["authored_utc", "sha", "author_name", "author_email", "subject"])

        while True:
            items = github_get_json(
                f"https://api.github.com/repos/{owner}/{repo}/commits",
                headers=headers,
                params={"since": since, "until": until, "per_page": 100, "page": page},
                timeout=30,
            )
            if not items:
                break

            for c in items:
                sha = c.get("sha")
                parents = c.get("parents", [])
                is_merge = len(parents) > 1
                if is_merge:
                    continue

                author = (c.get("commit", {}).get("author") or {})
                authored_utc = author.get("date")
                author_name = author.get("name")
                author_email = author.get("email")

                msg = c.get("commit", {}).get("message", "")
                subject = msg.splitlines()[0] if msg else ""

                writer.writerow([authored_utc, sha, author_name, author_email, subject])
                total += 1

            page += 1

    print(f"[OK] 总记录数: {total}")


if __name__ == "__main__":
    main()