import os
import pandas as pd
import csv

def main() -> None:
    # 1.获取原始csv
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    csv_path = os.path.join(repo_root, "data", "module_b", "commits.csv")

    if not csv_path:
        raise RuntimeError("请先运行scripts/module_b/get_git_data.py获取数据")

    cols = ["authored_utc", "author_name", "subject"]
    # 2. 过滤字段
    df = pd.read_csv(csv_path, usecols=cols)
    
    # 3. 过滤 Merge 提交
    df = df[~df['subject'].str.contains('Merge pull request|Merge branch', case=False, na=False)]

    # 4. 转换为北京时间
    df["authored_utc"] = pd.to_datetime(df["authored_utc"])
    df["time"] = df["authored_utc"] + pd.Timedelta(hours=8)
    
    # 5. 存入新的csv
    clean_csv_path = os.path.join(repo_root, "data", "module_b", "clean_commits.csv")

    df[["time", "author_name"]].to_csv(clean_csv_path, index=False, header=["time", "name"])

    print(f"[OK] 已清洗数据并保存至: {clean_csv_path}")

if __name__ == "__main__":
    main()