import os
import pandas as pd
import matplotlib.pyplot as plt
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
        print("\n节假日提交详情:")
        for d in holiday_days:
            print(d)

    # 4. 可视化
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False

    dates = daily_counts.index
    counts = daily_counts.values
    colors = ['red' if is_holiday(d) else 'skyblue' for d in dates]
    
    plt.figure(figsize=(15, 8))
    bars = plt.bar(dates, counts, color=colors)
    
    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color='red', lw=4),
                    Line2D([0], [0], color='skyblue', lw=4)]
    plt.legend(custom_lines, ['节假日', '工作日'])

    plt.title('每日提交统计 (节假日 vs 工作日)')
    plt.xlabel('日期')
    plt.ylabel('提交数量')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # 确保输出目录存在
    results_dir = os.path.join(repo_root, "figures", "module_b")
    os.makedirs(results_dir, exist_ok=True)
    
    output_path = os.path.join(results_dir, "overtime_analysis.png")
    plt.savefig(output_path)
    print(f"图表已保存至: {output_path}")

if __name__ == "__main__":
    main()
