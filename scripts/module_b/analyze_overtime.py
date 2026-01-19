import os
import pandas as pd
import matplotlib.pyplot as plt
from chinese_calendar import is_holiday
from matplotlib.patches import Patch

def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    csv_path = os.path.join(repo_root, "data", "module_b", "clean_commits.csv")

    if not os.path.exists(csv_path):
        raise RuntimeError(f"CSV 文件不存在: {csv_path}")

    cols = ["time"]
    df = pd.read_csv(csv_path, usecols=cols)

    # 预处理：聚合每日提交量
    df["time"] = pd.to_datetime(df["time"])
    df["date"] = df["time"].dt.date
    daily_counts = df["date"].value_counts().sort_index()

    print("\n=== 法定节假日/周末提交统计 ===")
    holiday_commits = 0
    holiday_days = []
    
    for date, count in daily_counts.items():
        if is_holiday(date):
            holiday_commits += count
            holiday_days.append(f"{date} ({count})")

    # 输出统计报告
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
    plt.bar(dates, counts, color=colors)
    
    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color='red', lw=4),
                    Line2D([0], [0], color='skyblue', lw=4)]
    plt.legend(custom_lines, ['节假日', '工作日'])

    plt.title('每日提交统计 (节假日 vs 工作日)')
    plt.xlabel('日期')
    plt.ylabel('提交数量')
    plt.xticks(rotation=45)
    plt.tight_layout()

    results_dir = os.path.join(repo_root, "figures", "module_b")
    os.makedirs(results_dir, exist_ok=True)
    
    output_path = os.path.join(results_dir, "overtime_analysis.png")
    plt.savefig(output_path)
    print(f"图表已保存至: {output_path}")

    # 节假日加班比例分析
    
    min_date = df["date"].min()
    max_date = df["date"].max()
    all_dates = pd.date_range(start=min_date, end=max_date).date
    
    holidays_worked = 0
    holidays_rested = 0
    worked_dates = set(daily_counts.index)
    
    for date in all_dates:
        if is_holiday(date):
            if date in worked_dates:
                holidays_worked += 1
            else:
                holidays_rested += 1
                
    # 绘制饼图
    plt.figure(figsize=(10, 8))
    labels = [f'加班节假日 ({holidays_worked}天)', f'休息节假日 ({holidays_rested}天)']
    sizes = [holidays_worked, holidays_rested]
    colors = ['#ff9999', '#99ff99'] 
    explode = (0.1, 0)
    wedges, texts, autotexts = plt.pie(sizes, explode=explode, labels=None, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=140)
    
    legend_elements = [Patch(facecolor=colors[0], label=labels[0]),
                       Patch(facecolor=colors[1], label=labels[1])]
            
    plt.legend(handles=legend_elements, title="统计详情", loc="center left", bbox_to_anchor=(0.85, 0.5))

            
    plt.title(f'节假日加班比例分析\n({min_date} ~ {max_date})')
    
    pie_path = os.path.join(results_dir, "overtime_pie_chart.png")
    plt.savefig(pie_path)
    print(f"饼图已保存至: {pie_path}")

if __name__ == "__main__":
    main()
