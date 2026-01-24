import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from chinese_calendar import is_workday
import matplotlib.dates as mdates

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False 

def main() -> None:
    # 1. 初始化路径
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    csv_path = os.path.join(repo_root, "data", "module_b", "clean_commits.csv")
    output_dir = os.path.join(repo_root, "figures", "module_b")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(csv_path):
        raise RuntimeError(f"CSV 文件不存在: {csv_path}")

    # 2. 读取与预处理数据
    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])
    
    df['hour'] = df['time'].dt.hour
    df['weekday'] = df['time'].dt.dayofweek
    df['date'] = df['time'].dt.date

    # 3. 计算节假日与加班标识
    unique_dates = df['date'].unique()
    workday_map = {d: is_workday(d) for d in unique_dates}
    
    df['is_workday'] = df['date'].map(workday_map)
    df['is_overtime'] = (~df['is_workday']) | ((df['is_workday']) & ((df['hour'] < 10) | (df['hour'] >= 19)))

    # 4. 绘制热力图
    plot_heatmap(df, output_dir)

def plot_heatmap(df, output_dir):
    print("正在绘制热力图...")
    heatmap_data = pd.crosstab(df['weekday'], df['hour'])
    
    heatmap_data = heatmap_data.reindex(index=range(7), columns=range(24), fill_value=0)
    weekday_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    heatmap_data.index = weekday_labels

    plt.figure(figsize=(16, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", annot=False, fmt="d", cbar_kws={'label': '提交数量'})
    
    plt.title('RocketMQ 代码提交热力图', fontsize=16)
    plt.xlabel('小时 (0-23)', fontsize=12)
    plt.ylabel('星期', fontsize=12)
    plt.tight_layout()
    
    out_path = os.path.join(output_dir, "commit_heatmap.png")
    plt.savefig(out_path, dpi=300)
    print(f"[OK] 热力图已保存: {out_path}")


if __name__ == "__main__":
    main()
