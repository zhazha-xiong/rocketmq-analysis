import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def setup_style():
    """配置绘图风格和中文字体"""
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    sns.set_theme(style="whitegrid", font="SimHei")

def load_data(json_path):
    if not os.path.exists(json_path):
        raise RuntimeError(f"数据文件缺失: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def plot_radar(data, save_path):
    """绘制雷达图展示四大维度得分占比"""

    categories = ['版本控制', '持续集成', '社区治理', '代码质量']
    max_scores = [25, 20, 30, 25]
    
    scores = [
        data['version_control']['total'],
        data['ci_health']['total'],
        data['governance']['total'],
        data['code_quality']['total']
    ]
    
    values = [s / m * 100 for s, m in zip(scores, max_scores)]
    values += values[:1]
    
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    plt.xticks(angles[:-1], categories, color='black', size=14)
    
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20%", "40%", "60%", "80%", "100%"], color="grey", size=10)
    plt.ylim(0, 100)
    
    ax.plot(angles, values, linewidth=2, linestyle='solid', label='得分率', color='#1f77b4')
    ax.fill(angles, values, '#1f77b4', alpha=0.25)
    
    plt.title(f"项目社区成熟度评分\n总分: {data['total_score']}/100", size=16, y=1.08)
    plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"[OK] 雷达图已保存: {save_path}")

def plot_breakdown(data, save_path):
    """绘制详细指标得分条形图"""

    breakdown = {
        '版本控制 (25)': {
            'Commit规范': (data['version_control']['commit_norm'], 15),
            'PR流程规范': (data['version_control']['pr_process'], 10)
        },
        '持续集成 (20)': {
            'CI运行成功率': (data['ci_health']['run_rate'], 15),
            'CI配置存在': (data['ci_health']['config_exist'], 5)
        },
        '社区治理 (30)': {
            '关键文档': (data['governance']['docs'], 15),
            '发布周期': (data['governance']['release_cycle'], 15)
        },
        '代码质量 (25)': {
            '测试配置': (data['code_quality']['test_config'], 10),
            '代码规范': (data['code_quality']['style_config'], 15)
        }
    }
    
    items = []
    scores = []
    max_vals = []
    colors = []
    cat_colors = sns.color_palette("muted", 4)
    
    for idx, (cat, sub) in enumerate(breakdown.items()):
        for name, (score, m_val) in sub.items():
            cat_name = cat.split(' ')[0]
            items.append(f"{cat_name}\n{name}")
            scores.append(score)
            max_vals.append(m_val)
            colors.append(cat_colors[idx])
            
    fig, ax = plt.subplots(figsize=(12, 8))
    
    y_pos = np.arange(len(items))
    
    ax.barh(y_pos, max_vals, align='center', color='#f0f0f0', label='该项满分', height=0.7)

    bars = ax.barh(y_pos, scores, align='center', color=colors, label='实际得分', height=0.5)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(items, fontsize=11)
    ax.invert_yaxis()
    ax.set_xlabel('得分', fontsize=12)
    ax.set_title('各细分指标得分详情', fontsize=15)
    
    for i, bar in enumerate(bars):
        width = bar.get_width()
        max_v = max_vals[i]
        label_x = width + 0.1 if width < max_v * 0.9 else width - 0.5 
        color = 'black' if width < max_v * 0.9 else 'white'
        ha = 'left' if width < max_v * 0.9 else 'right'
        
        ax.text(width + 0.2, bar.get_y() + bar.get_height()/2, 
                f'{scores[i]:.1f} / {max_v}', 
                va='center', fontsize=10, fontweight='bold', color='black')

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=cat_colors[i], label=cat) for i, cat in enumerate(breakdown.keys())]
    ax.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"[OK] 细分指标图已保存: {save_path}")

import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config_utils import load_config

CONFIG = load_config()

def main():

    data_dir = Path(CONFIG['paths']['data']) / "module_c"
    figs_dir = Path(CONFIG['paths']['figures']) / "module_c"
    
    data_path = data_dir / "clean_scores.json"
    fig_dir = str(figs_dir)
    os.makedirs(fig_dir, exist_ok=True)
    
    print(f"数据路径: {data_path}")
    print(f"输出目录: {fig_dir}")
    
    setup_style()
    try:
        data = load_data(str(data_path))
        plot_radar(data, os.path.join(fig_dir, "radar_chart.png"))
        plot_breakdown(data, os.path.join(fig_dir, "breakdown_chart.png"))
    except Exception as e:
        print(f"[Error] 可视化失败: {str(e)}")

if __name__ == "__main__":
    main()