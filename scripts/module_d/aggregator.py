"""
aggregator.py

职责：
- 将模块 A / B / C 的 REPORT.md 与图表信息进行结构化汇总
- 生成 AGGREGATED_REPORT.md，作为 LLM 的唯一事实输入
- 明确标注模块状态、缺失项与证据来源
"""

from pathlib import Path
from typing import Dict, List
from datetime import datetime
from utils import DATA_DIR, PROJECT_ROOT


# =========================
# 输出路径
# =========================

AGGREGATED_REPORT_PATH = DATA_DIR / "module_d/AGGREGATED_REPORT.md"


# =========================
# 核心函数
# =========================

def generate_aggregated_report(collected: Dict[str, dict]) -> Path:
    """
    根据 collector 的输出生成聚合报告

    Args:
        collected:
            collector.collect_outputs() 的返回结果

    Returns:
        AGGREGATED_REPORT.md 的路径
    """
    AGGREGATED_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with AGGREGATED_REPORT_PATH.open("w", encoding="utf-8") as f:
        _write_header(f)
        _write_execution_overview(f, collected)

        for module_name in ["module_a", "module_b", "module_c"]:
            _write_module_section(f, module_name, collected.get(module_name, {}))

    print(f"\n[Module D] Aggregated report generated at:")
    print(f"  {AGGREGATED_REPORT_PATH}")

    return AGGREGATED_REPORT_PATH


# =========================
# 写作函数
# =========================

def _write_header(f):
    f.write("# Aggregated Engineering Analysis Report\n\n")
    f.write(
        "本文件为模块 D 自动生成的**聚合证据报告**，"
        "仅包含来自模块 A / B / C 的原始结论、图表索引与执行状态。\n\n"
        "**注意**：本报告不包含任何新的分析或推断，"
        "是后续大模型综合解读的唯一事实来源。\n\n"
    )
    f.write(f"生成时间：{datetime.utcnow().isoformat()} UTC\n\n")
    f.write("---\n\n")


def _write_execution_overview(f, collected: Dict[str, dict]):
    """
    写执行概览
    """
    f.write("## 0. Pipeline Execution Overview\n\n")
    f.write("| Module | Executed | Success | REPORT.md | Figures | Issues |\n")
    f.write("|--------|----------|---------|-----------|---------|--------|\n")

    for name, info in collected.items():
        issues = "; ".join(info.get("issues", [])) or "None"
        f.write(
            f"| {name} | "
            f"{info.get('executed')} | "
            f"{info.get('success')} | "
            f"{info.get('report_exists')} | "
            f"{info.get('figures_count')} | "
            f"{issues} |\n"
        )

    f.write("\n---\n\n")


def _write_module_section(f, module_name: str, info: dict):
    """
    写单个模块的完整证据区块
    """
    title_map = {
        "module_a": "Module A – Code Quality & Risk",
        "module_b": "Module B – Development Efficiency & Rhythm",
        "module_c": "Module C – Governance & Engineering Practice",
    }

    f.write(f"## {title_map.get(module_name, module_name)}\n\n")

    # 状态块（固定结构）
    f.write("### Status\n\n")
    f.write(f"- Executed: `{info.get('executed')}`\n")
    f.write(f"- Success: `{info.get('success')}`\n")
    f.write(f"- REPORT.md exists: `{info.get('report_exists')}`\n")
    f.write(f"- Figures count: `{info.get('figures_count')}`\n")

    if info.get("issues"):
        f.write("- Issues:\n")
        for issue in info["issues"]:
            f.write(f"  - {issue}\n")
    else:
        f.write("- Issues: None\n")

    f.write("\n")

    # 图表索引
    f.write("### Figures Index\n\n")
    figures: List[str] = info.get("figures", [])
    if figures:
        for fig in figures:
            try:
                # 转换为相对于项目根目录的路径
                rel_path = Path(fig).relative_to(PROJECT_ROOT).as_posix()
                f.write(f"- `{rel_path}`\n")
            except ValueError:
                f.write(f"- `{fig}`\n")
    else:
        f.write("*(No figures available)*\n")

    f.write("\n")

    # 原始报告内容
    f.write("### Original Report Content\n\n")

    report_path = info.get("report_path")
    if report_path and Path(report_path).exists():
        content = Path(report_path).read_text(encoding="utf-8")
        f.write("```markdown\n")
        f.write(content.strip())
        f.write("\n```\n\n")
    else:
        f.write(
            "_Original REPORT.md is missing. "
            "No evidence is available for this module._\n\n"
        )

    f.write("---\n\n")
