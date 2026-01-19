import os
import pandas as pd
from chinese_calendar import is_workday
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

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

    print(f"\n=== 工作日加班详情 ===")
    print(f"有提交工作日总天数: {workday_df['date'].nunique()}")
    print(f"有加班记录天数: {len(daily_stats)}")
    print(f"工作日总提交: {len(workday_df)}")
    print(f"工作日加班提交: {len(overtime_df)}")
    if len(workday_df) > 0:
        print(f"加班提交占比: {len(overtime_df)/len(workday_df):.2%}")
    
    # 4. 可视化分析
    
    # 设置绘图风格与字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    
    results_dir = os.path.join(repo_root, "figures", "module_b")
    os.makedirs(results_dir, exist_ok=True)

    # 图表 1: 工作日提交的时间分布
    hourly_counts = workday_df["hour"].value_counts().reindex(range(24), fill_value=0).sort_index()
    
    hours = hourly_counts.index
    counts = hourly_counts.values

    colors = []
    for h in hours:
        if 10 <= h < 19:
            colors.append('skyblue')
        else:
            colors.append('#ff9999')
            
    plt.figure(figsize=(12, 6))
    bars = plt.bar(hours, counts, color=colors, edgecolor='grey', alpha=0.8)
    
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{int(height)}',
                     ha='center', va='bottom')

    # 添加辅助线
    plt.axvline(x=9.5, color='orange', linestyle='--', alpha=0.7)
    plt.axvline(x=18.5, color='orange', linestyle='--', alpha=0.7)
    plt.text(9.5, max(counts)*0.95, ' 上班 (10:00)', color='orange')
    plt.text(18.5, max(counts)*0.95, ' 下班 (19:00)', color='orange')

    # 图例
    legend_elements = [Patch(facecolor='skyblue', label='正常工时 (10:00-19:00)'),
                       Patch(facecolor='#ff9999', label='加班/早勤 (<10:00 或 ≥19:00)')]
    plt.legend(handles=legend_elements, loc='upper right')

    plt.title('工作日提交时间分布 (每小时提交量)')
    plt.xlabel('时间 (24小时制)')
    plt.ylabel('提交数量')
    plt.xticks(range(24))
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    bar_chart_path = os.path.join(results_dir, "workday_hourly_distribution.png")
    plt.savefig(bar_chart_path)
    print(f"时段分布图已保存至: {bar_chart_path}")

    # 图表 2: 工作日加班占比
    total_commits = len(workday_df)
    overtime_commits = len(overtime_df)
    normal_commits = total_commits - overtime_commits
    
    plt.figure(figsize=(10, 8))
    
    sizes = [overtime_commits, normal_commits]
    labels = [f'加班提交 ({overtime_commits})', f'正常工时 ({normal_commits})']
    pie_colors = ['#ff9999', 'skyblue']
    explode = (0.05, 0)
    
    wedges, texts, autotexts = plt.pie(sizes, explode=explode, labels=None, colors=pie_colors, 
                                       autopct='%1.1f%%', shadow=True, startangle=90)
    
    # 图例
    plt.legend(wedges, labels, title="工时类型", loc="center left", bbox_to_anchor=(0.85, 0.5))
    
    plt.title(f'工作日加班强度分析\n(样本总提交: {total_commits})')
    
    pie_chart_path = os.path.join(results_dir, "workday_overtime_pie.png")
    plt.savefig(pie_chart_path)
    print(f"加班占比图已保存至: {pie_chart_path}")

if __name__ == "__main__":
    main()
