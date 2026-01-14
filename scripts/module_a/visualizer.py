"""
生成模块A的可视化图表
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
from matplotlib.font_manager import FontProperties, findfont, FontManager

import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'SimSun']
matplotlib.rcParams['axes.unicode_minus'] = False

warnings.filterwarnings('ignore', category=UserWarning, message='.*Glyph.*missing.*')

sns.set_style("whitegrid")
sns.set_palette("husl")

def plot_bandit_severity(df_bandit, output_dir):
    """Plot Bandit issue severity distribution"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Severity distribution
    severity_counts = df_bandit['severity'].value_counts()
    ax1.pie(severity_counts.values, labels=severity_counts.index, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Security Issue Severity Distribution', fontsize=14, fontweight='bold')
    
    confidence_counts = df_bandit['confidence'].value_counts()
    ax2.pie(confidence_counts.values, labels=confidence_counts.index, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Security Issue Confidence Distribution', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'bandit_severity_distribution.png'), dpi=300, bbox_inches='tight')
    print(f"Generated: bandit_severity_distribution.png")
    plt.close()

def plot_bandit_issues(df_bandit, output_dir):
    """Plot Bandit issue types Top 10"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    issue_counts = df_bandit['issue_name'].value_counts().head(10)
    issue_counts.plot(kind='barh', ax=ax)
    
    ax.set_xlabel('Issue Count', fontsize=12)
    ax.set_ylabel('Issue Type', fontsize=12)
    ax.set_title('Top 10 Security Issue Types', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    
    for i, v in enumerate(issue_counts.values):
        ax.text(v + 0.5, i, str(v), va='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'bandit_top_issues.png'), dpi=300, bbox_inches='tight')
    print(f"Generated: bandit_top_issues.png")
    plt.close()

def plot_complexity_distribution(df_lizard, output_dir):
    """Plot code complexity distribution"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    sns.boxplot(data=df_lizard, y='ccn', ax=axes[0, 0])
    axes[0, 0].axhline(y=15, color='r', linestyle='--', label='Threshold=15')
    axes[0, 0].set_ylabel('Cyclomatic Complexity (CCN)', fontsize=12)
    axes[0, 0].set_title('CCN Distribution', fontsize=13, fontweight='bold')
    axes[0, 0].legend()
    
    sns.boxplot(data=df_lizard, y='nloc', ax=axes[0, 1])
    axes[0, 1].axhline(y=80, color='r', linestyle='--', label='Threshold=80')
    axes[0, 1].set_ylabel('Lines of Code (NLOC)', fontsize=12)
    axes[0, 1].set_title('Function Lines Distribution', fontsize=13, fontweight='bold')
    axes[0, 1].legend()
    
    sns.boxplot(data=df_lizard, y='param', ax=axes[1, 0])
    axes[1, 0].axhline(y=5, color='r', linestyle='--', label='Threshold=5')
    axes[1, 0].set_ylabel('Parameter Count', fontsize=12)
    axes[1, 0].set_title('Function Parameters Distribution', fontsize=13, fontweight='bold')
    axes[1, 0].legend()
    
    problem_counts = pd.Series({
        'High Complexity\n(CCN>15)': df_lizard['high_complexity'].sum(),
        'Too Long\n(NLOC>80)': df_lizard['too_long'].sum(),
        'Too Many Params\n(param>5)': df_lizard['too_many_params'].sum()
    })
    problem_counts.plot(kind='bar', ax=axes[1, 1], color=['#e74c3c', '#f39c12', '#9b59b6'])
    axes[1, 1].set_ylabel('Function Count', fontsize=12)
    axes[1, 1].set_title('Problem Function Statistics', fontsize=13, fontweight='bold')
    axes[1, 1].set_xticklabels(axes[1, 1].get_xticklabels(), rotation=0)
    
    for i, v in enumerate(problem_counts.values):
        axes[1, 1].text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'complexity_distribution.png'), dpi=300, bbox_inches='tight')
    print(f"Generated: complexity_distribution.png")
    plt.close()

def plot_top_complex_functions(df_lizard, output_dir, top_n=10):
    """绘制最复杂的函数排名"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    top_complex = df_lizard.nlargest(top_n, 'ccn')
    
    labels = [f"{row['repository'][:15]}...\n{row['function'][:30]}..." 
              if len(row['function']) > 30 
              else f"{row['repository'][:15]}...\n{row['function']}"
              for _, row in top_complex.iterrows()]
    
    y_pos = range(len(labels))
    ax.barh(y_pos, top_complex['ccn'].values)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Cyclomatic Complexity (CCN)', fontsize=12)
    ax.set_title(f'Top {top_n} Most Complex Functions', fontsize=14, fontweight='bold')
    
    for i, v in enumerate(top_complex['ccn'].values):
        ax.text(v + 0.5, i, str(v), va='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top_complex_functions.png'), dpi=300, bbox_inches='tight')
    print(f"Generated: top_complex_functions.png")
    plt.close()

def plot_repository_comparison(df_bandit, df_lizard, output_dir):
    """Compare code quality between two repositories"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    bandit_by_repo = df_bandit['repository'].value_counts()
    bandit_by_repo.plot(kind='bar', ax=axes[0], color=['#3498db', '#e74c3c'])
    axes[0].set_ylabel('Security Issue Count', fontsize=12)
    axes[0].set_title('Security Issues by Repository', fontsize=13, fontweight='bold')
    axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=0)
    
    max_value = bandit_by_repo.max()
    axes[0].set_ylim(0, max_value * 1.15)
    for i, v in enumerate(bandit_by_repo.values):
        axes[0].text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    lizard_by_repo = df_lizard.groupby('repository')['ccn'].mean()
    lizard_by_repo.plot(kind='bar', ax=axes[1], color=['#2ecc71', '#f39c12'])
    axes[1].set_ylabel('Average CCN', fontsize=12)
    axes[1].set_title('Average Complexity by Repository', fontsize=13, fontweight='bold')
    axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=0)

    max_value = lizard_by_repo.max()
    axes[1].set_ylim(0, max_value * 1.15)
    for i, v in enumerate(lizard_by_repo.values):
        axes[1].text(i, v + 0.2, f'{v:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'repository_comparison.png'), dpi=300, bbox_inches='tight')
    print(f"Generated: repository_comparison.png")
    plt.close()

if __name__ == "__main__":
    print("Loading data...")
    df_bandit = pd.read_csv("data/module_a/bandit_results.csv", encoding='utf-8-sig')
    df_lizard = pd.read_csv("data/module_a/lizard_results.csv", encoding='utf-8-sig')
    
    output_dir = "figures/module_a"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\nGenerating charts...")
    print("=" * 50)
    
    plot_bandit_severity(df_bandit, output_dir)
    plot_bandit_issues(df_bandit, output_dir)
    plot_complexity_distribution(df_lizard, output_dir)
    plot_top_complex_functions(df_lizard, output_dir)
    plot_repository_comparison(df_bandit, df_lizard, output_dir)
    
    print("\n" + "=" * 50)
    print(f"All charts generated and saved to: {output_dir}")