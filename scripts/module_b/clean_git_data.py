import os
import pandas as pd

def main() -> None:
    # 1.获取原始csv
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    csv_path = os.path.join(repo_root, "data", "module_b", "commits.csv")

    cols = ["authored_utc", "author_name"]
    # 2. 过滤字段
    df = pd.read_csv(csv_path, usecols=cols)
    
    # 转换为北京时间
    df["authored_utc"] = pd.to_datetime(df["authored_utc"])
    df["bj_time"] = df["authored_utc"] + pd.Timedelta(hours=8)
    
    print(df[["beijing_time", "author_name"]].head())


if __name__ == "__main__":
    main()