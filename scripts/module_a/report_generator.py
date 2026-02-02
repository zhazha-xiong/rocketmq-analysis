import os
import sys
from typing import Iterable, Tuple

import pandas as pd

scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from report_utils import get_repo_root, now_str, write_text
from module_utils import write_report


def _safe_pct(numerator: int, denominator: int) -> float:
    """安全的百分比计算，分母为0时返回0"""
    return (numerator / denominator * 100.0) if denominator else 0.0


def _md_table(rows: Iterable[Tuple[str, str]]) -> str:
    """生成Markdown表格"""
    lines = ["| 指标 | 值 |", "| --- | --- |"]
    for k, v in rows:
        lines.append(f"| {k} | {v} |")
    return "\n".join(lines)


def load_data(
    python_files_path: str,
    bandit_results_path: str,
    lizard_results_path: str
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """加载模块A的三个主要数据文件"""
    
    if not os.path.exists(python_files_path):
        raise RuntimeError(f"文件扫描数据不存在: {python_files_path}")
    if not os.path.exists(bandit_results_path):
        raise RuntimeError(f"Bandit扫描结果不存在: {bandit_results_path}")
    if not os.path.exists(lizard_results_path):
        raise RuntimeError(f"Lizard分析结果不存在: {lizard_results_path}")
    
    df_files = pd.read_csv(python_files_path)
    df_bandit = pd.read_csv(bandit_results_path)
    df_lizard = pd.read_csv(lizard_results_path)
    
    return df_files, df_bandit, df_lizard


def build_markdown(
    df_files: pd.DataFrame,
    df_bandit: pd.DataFrame,
    df_lizard: pd.DataFrame,
    *,
    figures_rel_dir: str
) -> str:
    
    generated_at = now_str()
    
    # 基础统计
    total_files = int(len(df_files))
    
    # Bandit统计
    total_issues = int(len(df_bandit))
    high_severity = int((df_bandit['issue_severity'] == 'HIGH').sum()) if not df_bandit.empty else 0
    medium_severity = int((df_bandit['issue_severity'] == 'MEDIUM').sum()) if not df_bandit.empty else 0
    low_severity = int((df_bandit['issue_severity'] == 'LOW').sum()) if not df_bandit.empty else 0
    
    high_pct = _safe_pct(high_severity, total_issues)
    medium_pct = _safe_pct(medium_severity, total_issues)
    
    # Lizard统计
    high_complexity_funcs = int((df_lizard['ccn'] > 15).sum()) if not df_lizard.empty else 0
    long_funcs = int((df_lizard['nloc'] > 80).sum()) if not df_lizard.empty else 0
    many_params_funcs = int((df_lizard['param'] > 5).sum()) if not df_lizard.empty else 0
    
    total_funcs = int(len(df_lizard))
    high_complexity_pct = _safe_pct(high_complexity_funcs, total_funcs)
    
    avg_complexity = float(df_lizard['ccn'].mean()) if not df_lizard.empty else 0.0
    avg_nloc = float(df_lizard['nloc'].mean()) if not df_lizard.empty else 0.0
    
    # 按仓库统计
    repo_stats_files = df_files.groupby('repository').size().to_dict() if 'repository' in df_files.columns else {}
    repo_stats_issues = df_bandit.groupby('repository').size().to_dict() if 'repository' in df_bandit.columns and not df_bandit.empty else {}
    
    # 构建指标表格
    metrics = _md_table([
        ("扫描Python文件总数", str(total_files)),
        ("检测到的潜在安全问题总数", str(total_issues)),
        ("高危问题数量（HIGH）", f"{high_severity} ({high_pct:.1f}%)"),
        ("中危问题数量（MEDIUM）", f"{medium_severity} ({medium_pct:.1f}%)"),
        ("低危问题数量（LOW）", str(low_severity)),
        ("分析函数总数", str(total_funcs)),
        ("高复杂度函数（CCN > 15）", f"{high_complexity_funcs} ({high_complexity_pct:.1f}%)"),
        ("过长函数（NLOC > 80）", str(long_funcs)),
        ("参数过多函数（参数 > 5）", str(many_params_funcs)),
        ("平均圈复杂度", f"{avg_complexity:.2f}"),
        ("平均函数行数（NLOC）", f"{avg_nloc:.2f}"),
    ])
    
    # 仓库对比表格
    repo_comparison_lines = ["| 仓库 | Python文件数 | 潜在问题数 |", "| --- | --- | --- |"]
    for repo in repo_stats_files.keys():
        file_count = repo_stats_files.get(repo, 0)
        issue_count = repo_stats_issues.get(repo, 0)
        repo_name = repo.split('/')[-1] if '/' in repo else repo
        repo_comparison_lines.append(f"| {repo_name} | {file_count} | {issue_count} |")
    repo_comparison = "\n".join(repo_comparison_lines)
    
    # 图表路径生成函数
    fig = lambda filename: f"{figures_rel_dir}/{filename}"
    
    # 构建报告
    report = [
        "# 模块 A：代码质量与潜在风险（Python 客户端）",
        "",
        f"生成时间：{generated_at}",
        "评估对象：Apache RocketMQ (GitHub)",
        "",
        "## 1. 分析范围",
        "- 仓库：",
        "  - `apache/rocketmq-client-python`（官方Python客户端）",
        "  - `apache/rocketmq-clients/python`（新一代多语言客户端的Python实现）",
        "- 分析工具：",
        "  - **Bandit**：安全漏洞静态分析",
        "  - **Lizard**：代码复杂度度量",
        "- 分析对象：所有`.py`文件（排除测试文件和第三方库）",
        "",
        "## 2. 关键结论",
        f"- 共扫描 **{total_files}** 个Python文件，检测到 **{total_issues}** 个潜在安全问题。",
        f"- 高危问题（HIGH）占比 **{high_pct:.1f}%**（{high_severity}/{total_issues}），中危问题（MEDIUM）占比 **{medium_pct:.1f}%**（{medium_severity}/{total_issues}）。",
        f"- 代码复杂度分析：共 **{total_funcs}** 个函数，其中高复杂度函数（CCN > 15）占比 **{high_complexity_pct:.1f}%**（{high_complexity_funcs}/{total_funcs}）。",
        f"- 平均圈复杂度为 **{avg_complexity:.2f}**，平均函数行数为 **{avg_nloc:.2f}** 行。",
        f"- 发现 **{long_funcs}** 个过长函数（NLOC > 80）和 **{many_params_funcs}** 个参数过多的函数（参数 > 5）。",
        "",
        "### 2.1 关键指标汇总",
        metrics,
        "",
        "### 2.2 仓库对比",
        repo_comparison,
        "",
        "## 3. 图表与解读",
        f"![安全问题严重性分布]({fig('bandit_severity_distribution.png')})",
        f"- 展示Bandit检测到的安全问题按严重性等级（HIGH/MEDIUM/LOW）的分布情况；高危和中危问题合计占比 {high_pct + medium_pct:.1f}%。",
        "",
        f"![TOP 10 安全问题类型]({fig('bandit_top_issues.png')})",
        "- 展示最常见的10种安全问题类型及其出现次数；可用于识别代码中的典型风险模式。",
        "",
        f"![函数复杂度分布]({fig('complexity_distribution.png')})",
        f"- 展示所有函数的圈复杂度（CCN）分布；复杂度大于15的函数占比 {high_complexity_pct:.1f}%，需重点关注。",
        "",
        f"![TOP 10 最复杂函数]({fig('top_complex_functions.png')})",
        "- 列出复杂度最高的10个函数；这些函数建议优先进行重构或增加单元测试覆盖。",
        "",
        f"![仓库质量对比]({fig('repository_comparison.png')})",
        "- 对比两个仓库的文件数、问题数和平均复杂度；帮助识别质量差异较大的子项目。",
        "",
        "## 4. 局限性与改进方向",
        "- Bandit基于AST静态分析，可能存在误报（False Positive）；部分告警需要人工复核确认实际风险。",
        "- Lizard的复杂度阈值（CCN > 15）为经验值，实际项目可根据团队规范调整。",
        "- 本分析仅针对Python代码，不包含C++扩展模块或其他语言实现。",
        "- 未对测试代码和文档进行分析，统计结果仅反映生产代码质量。",
    ]
    
    return "\n".join(report) + "\n"


def main() -> None:
    """主函数：加载数据、生成报告"""
    repo_root = get_repo_root(__file__)
    
    python_files_path = os.path.join(repo_root, "data", "module_a", "python_files.csv")
    bandit_results_path = os.path.join(repo_root, "data", "module_a", "bandit_results.csv")
    lizard_results_path = os.path.join(repo_root, "data", "module_a", "lizard_results.csv")
    report_path = os.path.join(repo_root, "data", "module_a", "REPORT.md")
    
    figures_rel_dir = "../../figures/module_a"
    
    df_files, df_bandit, df_lizard = load_data(
        python_files_path,
        bandit_results_path,
        lizard_results_path
    )
    
    md = build_markdown(df_files, df_bandit, df_lizard, figures_rel_dir=figures_rel_dir)
    write_report(report_path, md, module_label="模块 A")


if __name__ == "__main__":
    main()
