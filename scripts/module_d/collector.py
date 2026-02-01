"""
collector.py

负责：
- 校验模块 A / B / C 的交付物完整性
- 只检查 REPORT.md 和 figures，不解析原始数据
- 生成统一、可供聚合与 LLM 使用的结构化状态
"""

from pathlib import Path
from typing import Dict, List
from utils import DATA_DIR, FIGURES_DIR


# =========================
# 路径约定
# =========================

MODULES = {
    "module_a": {
        "report": DATA_DIR / "module_a/REPORT.md",
        "figures": FIGURES_DIR / "module_a",
    },
    "module_b": {
        "report": DATA_DIR / "module_b/REPORT.md",
        "figures": FIGURES_DIR / "module_b",
    },
    "module_c": {
        "report": DATA_DIR / "module_c/REPORT.md",
        "figures": FIGURES_DIR / "module_c",
    },
}


# =========================
# 核心函数
# =========================

def collect_outputs(run_results: Dict[str, dict]) -> Dict[str, dict]:
    """
    收集并校验模块 A / B / C 的交付物

    Args:
        run_results:
            runner.run_modules() 的返回结果

    Returns:
        {
            "module_a": {
                "executed": True,
                "success": True,
                "report_exists": True,
                "report_path": "data/module_a/REPORT.md",
                "figures": [
                    "figures/module_a/bandit_summary.png",
                    ...
                ],
                "issues": []
            },
            ...
        }
    """
    collected = {}

    print("\n" + "=" * 60)
    print("[Module D] Collecting module outputs")
    print("=" * 60)

    for name, paths in MODULES.items():
        print(f"\n[Module D] Checking {name} deliverables...")

        run_info = run_results.get(name, {})
        report_path = paths["report"]
        figures_dir = paths["figures"]

        figures = _collect_figures(figures_dir)

        issues = []
        if not report_path.exists():
            issues.append("REPORT.md missing")

        if report_path.exists() and report_path.stat().st_size == 0:
            issues.append("REPORT.md is empty")

        if figures_dir.exists() and not figures:
            issues.append("No figures found")

        collected[name] = {
            # 来自 runner 的信息（事实）
            "executed": run_info.get("executed", False),
            "success": run_info.get("success", False),
            "exit_code": run_info.get("exit_code"),

            # 交付物信息（collector 的核心职责）
            "report_exists": report_path.exists(),
            "report_path": str(report_path),
            "figures": figures,
            "figures_count": len(figures),

            # 诊断信息
            "issues": issues,
        }

        _print_summary(name, collected[name])

    return collected


# =========================
# 辅助函数
# =========================

def _collect_figures(figures_dir: Path) -> List[str]:
    """
    收集指定目录下的 PNG 图表路径
    """
    if not figures_dir.exists():
        return []

    return sorted(
        str(p)
        for p in figures_dir.glob("*.png")
        if p.is_file()
    )


def _print_summary(name: str, info: dict):
    """
    控制台友好输出
    """
    print(f"[Module D] {name} deliverable summary:")
    print(f"  - executed       : {info['executed']}")
    print(f"  - success        : {info['success']}")
    print(f"  - report_exists  : {info['report_exists']}")
    print(f"  - figures_count  : {info['figures_count']}")

    if info["issues"]:
        print("  - issues:")
        for issue in info["issues"]:
            print(f"      * {issue}")
    else:
        print("  - issues         : none")


# =========================
# CLI 调试入口（可选）
# =========================

if __name__ == "__main__":
    # 用于单独调试 collector（假定 runner 已跑过）
    dummy_run_results = {}
    collect_outputs(dummy_run_results)
