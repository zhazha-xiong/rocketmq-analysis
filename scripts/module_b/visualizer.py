import os
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from chinese_calendar import is_workday
from matplotlib.patches import Patch
import matplotlib.dates as mdates

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config_utils import load_config

CONFIG = load_config()

def setup_style():
    """配置绘图风格和中文字体"""
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    sns.set_theme(style="whitegrid", font="SimHei")

def load_and_process_data(csv_path):
    """读取并预处理数据"""
    if not os.path.exists(csv_path):
        raise RuntimeError(f"CSV 文件不存在: {csv_path}")

    print("正在加载和处理数据...")
    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])

    df['hour'] = df['time'].dt.hour
    df['weekday'] = df['time'].dt.dayofweek
    df['date'] = df['time'].dt.date
    
    unique_dates = df['date'].unique()
    workday_map = {d: is_workday(d) for d in unique_dates}
    
    df['is_workday'] = df['date'].map(workday_map)
    
    # 定义加班: 
    # 1. 节假日/周末 (非工作日)
    # 2. 工作日但时间在 10:00 之前或 19:00 之后
    df['is_overtime'] = (~df['is_workday']) | \
                        ((df['is_workday']) & ((df['hour'] < 10) | (df['hour'] >= 19)))
    
    return df

def plot_holiday_overtime_pie(df, output_dir):
    """绘制节假日加班占比饼图"""
    print("绘制: 节假日加班占比...")
    
    holiday_mask = ~df["is_workday"]
    is_holiday_commit = holiday_mask
    
    counts = is_holiday_commit.value_counts()
    
    # 确保有 True/False 两个键
    if True not in counts: counts[True] = 0
    if False not in counts: counts[False] = 0

    sizes = [counts[False], counts[True]]
    colors = ['#87CEEB', '#F08080']

    plt.figure(figsize=(12, 8))
    wedges, texts, autotexts = plt.pie(sizes, colors=colors, autopct='%1.1f%%', 
                                     startangle=90, explode=(0, 0.05), shadow=True)
    
    plt.setp(texts, size=10)
    plt.setp(autotexts, size=10)
    
    plt.title(f"节假日与周末加班提交分布\n(样本总提交: {len(df)})", fontsize=14)

    legend_labels = [f"工作日提交 ({counts[False]})", f"节假日/周末加班 ({counts[True]})"]
    plt.legend(wedges, legend_labels, title="提交类型", loc="center left", bbox_to_anchor=(0.85, 0, 0.5, 1))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "overtime_holiday_pie.png"), dpi=300)
    plt.close()

def plot_workday_overtime_pie(df, output_dir):
    """绘制工作日加班占比饼图"""
    print("绘制: 工作日加班占比...")
    
    workday_df = df[df['is_workday']].copy()
    
    overtime_mask = (workday_df['hour'] < 10) | (workday_df['hour'] >= 19)
    
    counts = overtime_mask.value_counts()
    if True not in counts: counts[True] = 0
    if False not in counts: counts[False] = 0

    sizes = [counts[False], counts[True]]
    colors = ['#87CEEB', '#F08080']
    plt.figure(figsize=(12, 8))
    wedges, texts, autotexts = plt.pie(sizes, colors=colors, autopct='%1.1f%%', 
                                     startangle=90, explode=(0, 0.05), shadow=True)
    
    plt.setp(texts, size=10)
    plt.setp(autotexts, size=10)
    
    plt.title(f"工作日加班强度分析\n(样本总提交: {len(workday_df)})", fontsize=14)
    
    legend_labels = [f"正常工时 ({counts[False]})", f"加班提交 ({counts[True]})"]
    plt.legend(wedges, legend_labels, title="工时类型", loc="center left", bbox_to_anchor=(0.85, 0, 0.5, 1))

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "overtime_workday_pie.png"), dpi=300)
    plt.close()

def plot_workday_hourly_bar(df, output_dir):
    """绘制工作日提交小时分布柱状图"""
    print("绘制: 工作日小时分布...")
    
    workday_df = df[df['is_workday']]
    hourly_counts = workday_df['hour'].value_counts().sort_index()
    
    full_index = pd.Index(range(24), name='hour')
    hourly_counts = hourly_counts.reindex(full_index, fill_value=0)
    
    bar_colors = ['#F08080' if (h < 10 or h >= 19) else '#87CEEB' for h in hourly_counts.index]
    
    plt.figure(figsize=(14, 7))
    bars = plt.bar(hourly_counts.index, hourly_counts.values, color=bar_colors, edgecolor='grey', alpha=0.8)
    
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{int(height)}',
                     ha='center', va='bottom', fontsize=9)

    plt.title("工作日提交时间分布 (每小时提交量)", fontsize=16)
    plt.xlabel("时间 (24小时制)", fontsize=12)
    plt.ylabel("提交数量", fontsize=12)
    plt.xticks(range(0, 24))

    plt.axvline(x=9.5, color='orange', linestyle='--', linewidth=1.5, alpha=0.8)
    plt.axvline(x=18.5, color='orange', linestyle='--', linewidth=1.5, alpha=0.8)
    
    plt.text(9.6, plt.ylim()[1]*0.9, '上班 (10:00)', color='orange', fontweight='bold')
    plt.text(18.6, plt.ylim()[1]*0.9, '下班 (19:00)', color='orange', fontweight='bold')

    legend_elements = [
        Patch(facecolor='#87CEEB', edgecolor='grey', label='正常工时 (10:00-19:00)'),
        Patch(facecolor='#F08080', edgecolor='grey', label='加班/早勤 (<10:00 或 >=19:00)')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "overtime_workday_bar.png"), dpi=300)
    plt.close()

def plot_heatmap(df, output_dir):
    """绘制周x小时热力图"""
    print("绘制: 提交热力图...")
    
    heatmap_data = pd.crosstab(df['weekday'], df['hour'])
    heatmap_data = heatmap_data.reindex(index=range(7), columns=range(24), fill_value=0)
    
    weekday_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    heatmap_data.index = weekday_labels
    
    plt.figure(figsize=(16, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", annot=False, fmt="d", cbar_kws={'label': '提交数量'})
    
    plt.title('代码提交热力图 (周 × 小时)', fontsize=16)
    plt.xlabel('小时 (0-23)', fontsize=12)
    plt.ylabel('星期', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "commit_heatmap.png"), dpi=300)
    plt.close()

def plot_daily_trend(df, output_dir):
    """绘制日提交趋势堆叠图(区分工作日/节假日)"""
    print("绘制: 每日提交趋势...")
    
    # 按日期聚合
    daily_stats = df.groupby(['date', 'is_workday']).size().unstack(fill_value=0)
    
    if True not in daily_stats.columns: daily_stats[True] = 0
    if False not in daily_stats.columns: daily_stats[False] = 0
    
    # 重命名列
    daily_stats = daily_stats.rename(columns={True: 'Workday', False: 'Holiday'})
    
    plt.figure(figsize=(16, 8))

    plt.bar(daily_stats.index, daily_stats['Workday'], label='工作日提交', color='white', edgecolor='#cccccc', width=1.0)
    plt.bar(daily_stats.index, daily_stats['Holiday'], bottom=daily_stats['Workday'], label='节假日/周末提交', color='#ff9999', edgecolor='none', width=1.0)
    
    plt.title('RocketMQ 每日代码提交趋势 (工作日 vs 节假日)', fontsize=16)
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('提交数量', fontsize=12)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.xticks(rotation=45)
    
    plt.legend(loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "daily_commit_trend.png"), dpi=300)
    plt.close()

def main():
    setup_style()
    
    data_dir = Path(CONFIG['paths']['data']) / "module_b"
    figs_dir = Path(CONFIG['paths']['figures']) / "module_b"
    csv_path = data_dir / "clean_commits.csv"
    output_dir = str(figs_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        df = load_and_process_data(str(csv_path))
        
        plot_holiday_overtime_pie(df, output_dir)
        plot_workday_overtime_pie(df, output_dir)
        plot_workday_hourly_bar(df, output_dir)
        plot_heatmap(df, output_dir)
        plot_daily_trend(df, output_dir)
        
        print(f"\n[OK] 所有图表已生成至: {output_dir}")
        
    except Exception as e:
        print(f"[Error] 绘图失败: {e}")

if __name__ == "__main__":
    main()
