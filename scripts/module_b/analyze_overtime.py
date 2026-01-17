import os
import pandas as pd
import csv

def main() -> None:
    # 1.获取csv
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    csv_path = os.path.join(repo_root, "data", "module_b", "clean_commits.csv")

    if not csv_path:
        raise RuntimeError("data/module_b/clean_commits.csv不存在")

    cols = ["time", "name"]
   
    df = pd.read_csv(csv_path, usecols=cols)

    # 2. 按天聚合
    df["time"] = pd.to_datetime(df["time"])
    
    df["date"] = df["time"].dt.date
    
    daily_counts = df["date"].value_counts().sort_index()

    print("=== 每日提交统计 ===")
    print(daily_counts)


if __name__ == "__main__":
    main()
