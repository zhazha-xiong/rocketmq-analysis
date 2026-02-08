"""
runner.py

负责串行运行模块 A / B / C 的 main.py
特点：
- 严格按 A → B → C 顺序执行
- 不因单个模块失败而中断（支持降级）
- 统一输出结构化执行状态，供模块 D 后续使用
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Dict
from utils import PROJECT_ROOT, DATA_DIR, FIGURES_DIR


# =========================
# 模块运行配置
# =========================

MODULES = [
    {
        "name": "module_a",
        "entry": PROJECT_ROOT / "scripts/module_a/main.py",
        "report": DATA_DIR / "module_a/REPORT.md",
        "figures": FIGURES_DIR / "module_a",
    },
    {
        "name": "module_b",
        "entry": PROJECT_ROOT / "scripts/module_b/main.py",
        "report": DATA_DIR / "module_b/REPORT.md",
        "figures": FIGURES_DIR / "module_b",
    },
    {
        "name": "module_c",
        "entry": PROJECT_ROOT / "scripts/module_c/main.py",
        "report": DATA_DIR / "module_c/REPORT.md",
        "figures": FIGURES_DIR / "module_c",
    },
]


# =========================
# 核心函数
# =========================

def run_modules() -> Dict[str, dict]:
    """
    串行运行模块 A / B / C，并返回每个模块的执行状态

    Returns:
        {
            "module_a": {
                "executed": True,
                "exit_code": 0,
                "report_exists": True,
                "figures_count": 3,
                "duration_sec": 12.3
            },
            ...
        }
    """
    results = {}

    print("=" * 60)
    print("[Module D] Starting pipeline: A → B → C")
    print("=" * 60)

    for module in MODULES:
        name = module["name"]
        entry = module["entry"]

        print(f"\n[Module D] Running {name} ...")

        start_time = time.time()

        if not entry.exists():
            print(f"[ERROR] Entry script not found: {entry}")
            results[name] = _build_result(
                executed=False,
                exit_code=None,
                module=module,
                duration=0.0,
            )
            continue
        
        # 使用当前 Python 解释器运行模块入口脚本
        try:
            proc = subprocess.run(
                [sys.executable, str(entry)],
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
            exit_code = proc.returncode
        except Exception as e:
            print(f"[ERROR] Failed to execute {name}: {e}")
            exit_code = -1

        duration = time.time() - start_time

        results[name] = _build_result(
            executed=True,
            exit_code=exit_code,
            module=module,
            duration=duration,
        )

        _print_summary(name, results[name])

    print("\n" + "=" * 60)
    print("[Module D] Pipeline finished")
    print("=" * 60)

    return results


# =========================
# 辅助函数
# =========================

def _build_result(executed: bool, exit_code, module: dict, duration: float) -> dict:
    """
    构建单个模块的执行结果字典
    """
    report_exists = module["report"].exists()
    figures_count = (
        len(list(module["figures"].glob("*.png")))
        if module["figures"].exists()
        else 0
    )

    return {
        "executed": executed,
        "exit_code": exit_code,
        "success": executed and exit_code == 0,
        "report_exists": report_exists,
        "figures_count": figures_count,
        "duration_sec": round(duration, 2),
        "report_path": str(module["report"]),
        "figures_path": str(module["figures"]),
    }


def _print_summary(name: str, result: dict):
    """
    打印模块执行摘要（用户友好）
    """
    status = "SUCCESS" if result["success"] else "FAILED"

    print(f"[Module D] {name} status: {status}")
    print(f"  - executed       : {result['executed']}")
    print(f"  - exit_code      : {result['exit_code']}")
    print(f"  - report_exists  : {result['report_exists']}")
    print(f"  - figures_count  : {result['figures_count']}")
    print(f"  - duration (sec) : {result['duration_sec']}")

if __name__ == "__main__":
    run_modules()
