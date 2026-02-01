import os
import csv

from datetime import datetime, timezone

from module_utils import github_get_json, github_headers, load_github_token, repo_root_from


def main() -> None:
    token = load_github_token(missing_hint="请在scripts/.env填写GITHUB_TOKEN", caller_file=__file__)

    owner, repo = "apache", "rocketmq"
    since = "2013-03-15T00:00:00Z"
    
    until = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    headers = github_headers(token)

    page = 1
    total = 0

    repo_root = repo_root_from(__file__)
    out_path = os.path.join(repo_root, "data", "module_b", "commits.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    print("===开始采集数据===")

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