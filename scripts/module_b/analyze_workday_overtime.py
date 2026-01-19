import os
import pandas as pd
from chinese_calendar import is_workday

def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    csv_path = os.path.join(repo_root, "data", "module_b", "clean_commits.csv")

    if not os.path.exists(csv_path):
        raise RuntimeError(f"CSV 文件不存在: {csv_path}")

    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])
    
    df["date"] = df["time"].dt.date
    df["hour"] = df["time"].dt.hour

    # 1. 筛选出工作日
    print("正在筛选工作日数据...")
    unique_dates = df["date"].unique()
    workday_map = {d: is_workday(d) for d in unique_dates}
    df["is_workday"] = df["date"].map(workday_map)
    
    workday_df = df[df["is_workday"]].copy()

    # 2. 定义加班时间：早于10点 或 晚于19点
    overtime_mask = (workday_df["hour"] < 10) | (workday_df["hour"] >= 19)
    overtime_df = workday_df[overtime_mask]

    # 3. 按日期聚合输出
    daily_stats = overtime_df.groupby("date").agg(
        commit_count=("time", "count"),
        hours=("hour", lambda x: sorted(list(x)))
    ).sort_index()

    print(f"\n=== 工作日加班详情 (正常工时: 10:00-19:00) ===")
    print(f"工作日总天数(有提交): {workday_df['date'].nunique()}")
    print(f"有加班记录天数: {len(daily_stats)}")
    print(f"工作日总提交: {len(workday_df)}")
    print(f"工作日加班提交: {len(overtime_df)}")
    if len(workday_df) > 0:
        print(f"加班提交占比: {len(overtime_df)/len(workday_df):.2%}")
    
    print("\n--- 每日详情 (日期 | 此日加班提交数 | 涉及时间点) ---")
    for date, row in daily_stats.iterrows():
        hours_str = ", ".join([f"{h}点" for h in row['hours']])
        print(f"{date} | {row['commit_count']} 次 \t| {hours_str}")

if __name__ == "__main__":
    main()
