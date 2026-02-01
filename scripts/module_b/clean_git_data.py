import os

import pandas as pd


def clean_commits_csv(csv_path: str, clean_csv_path: str) -> None:
    if not os.path.exists(csv_path):
        raise RuntimeError("请先运行scripts/module_b/get_git_data.py获取数据")

    cols = ["authored_utc", "author_name", "subject"]
    df = pd.read_csv(csv_path, usecols=cols)

    df = df[~df["subject"].str.contains("Merge pull request|Merge branch", case=False, na=False)]

    df["authored_utc"] = pd.to_datetime(df["authored_utc"])
    df["time"] = df["authored_utc"] + pd.Timedelta(hours=8)

    df[["time", "author_name"]].to_csv(clean_csv_path, index=False, header=["time", "name"])


def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    csv_path = os.path.join(repo_root, "data", "module_b", "commits.csv")
    clean_csv_path = os.path.join(repo_root, "data", "module_b", "clean_commits.csv")

    clean_commits_csv(csv_path, clean_csv_path)
    print(f"[OK] 已清洗数据并保存至: {clean_csv_path}")

if __name__ == "__main__":
    main()