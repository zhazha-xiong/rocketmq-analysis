import os
import sys
from pathlib import Path
import pandas as pd

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config_utils import load_config

CONFIG = load_config()

def clean_commits_csv(csv_path: str, clean_csv_path: str) -> None:
    """清洗 commits.csv 数据，保留需要的列并处理时间格式"""
    if not os.path.exists(csv_path):
        raise RuntimeError("请先运行scripts/module_b/get_git_data.py获取数据")


    cols = ["authored_utc", "author_name", "subject"]
    df = pd.read_csv(csv_path, usecols=cols)

    df = df[~df["subject"].str.contains("Merge pull request|Merge branch", case=False, na=False)]

    df["authored_utc"] = pd.to_datetime(df["authored_utc"])
    df["time"] = df["authored_utc"] + pd.Timedelta(hours=8)

    df[["time", "author_name"]].to_csv(clean_csv_path, index=False, header=["time", "name"])


def main() -> None:
    """运行 Module B 的数据清洗流程"""
    data_dir = Path(CONFIG['paths']['data']) / "module_b"
    csv_path = data_dir / "commits.csv"
    clean_csv_path = data_dir / "clean_commits.csv"

    clean_commits_csv(str(csv_path), str(clean_csv_path))
    print(f"[OK] 已清洗数据并保存至: {clean_csv_path}")

if __name__ == "__main__":
    main()