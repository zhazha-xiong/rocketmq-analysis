import os

import requests
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("请在scripts/module_b/.env填写GITHUB_TOKEN")

    owner, repo = "apache", "rocketmq"
    since = "2024-01-01T00:00:00Z"
    until = "2026-01-01T00:00:00Z"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    page = 1
    total = 0
    while True:
        r = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/commits",
            headers=headers,
            params={"since": since, "until": until, "per_page": 100, "page": page},
            timeout=30,
        )
        r.raise_for_status()
        items = r.json()
        if not items:
            break

        for c in items:
            sha = c.get("sha")
            parents = c.get("parents", [])
            is_merge = len(parents) > 1
            author = (c.get("commit", {}).get("author") or {})
            authored_utc = author.get("date")
            author_name = author.get("name")
            msg = c.get("commit", {}).get("message", "")
            subject = msg.splitlines()[0] if msg else ""

            print(f"{authored_utc}\t{sha}\tmerge={int(is_merge)}\t{author_name}\t{subject}")
            total += 1

        page += 1

    print(f"\n[OK] printed commits: {total}")


if __name__ == "__main__":
    main()