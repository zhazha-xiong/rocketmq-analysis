import os
import pandas as pd
from chinese_calendar import is_holiday

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

    # 3. 筛选出中国法定节假日提交
    print("\n=== 法定节假日/周末提交统计 ===")
    holiday_commits = 0
    holiday_days = []
    
    for date, count in daily_counts.items():
        if is_holiday(date):
            holiday_commits += count
            holiday_days.append(f"{date} ({count})")

    # 打印法定节假日提交数
    print(f"节假日提交总数: {holiday_commits}")
    print(f"节假日提交占比: {holiday_commits / daily_counts.sum():.2%}")
    if holiday_days:
        print("\n节假日提交详情 (前10条):")
        for d in holiday_days[:10]:
            print(d)
        if len(holiday_days) > 10:
            print(f"... 以及其他 {len(holiday_days) - 10} 天")


if __name__ == "__main__":
    main()
