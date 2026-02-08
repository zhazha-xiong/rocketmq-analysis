"""
main.py

模块 D 统一入口：
- 串行运行模块 A / B / C
- 校验并收集交付物
- 生成聚合证据报告
- （可选）调用 LLM 生成 FINAL_REPORT.md
"""

import sys
from pathlib import Path

from runner import run_modules
from collector import collect_outputs
from aggregator import generate_aggregated_report
from utils import OUTPUT_DIR

# LLM 调用是可选的，失败也允许系统继续运行
try:
    from llm_client import call_llm
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


# =========================
# 路径约定


FINAL_REPORT_PATH = OUTPUT_DIR / "FINAL_REPORT.md"


# =========================
# 主流程
# =========================

def main():
    print("\n" + "=" * 70)
    print(" RocketMQ Engineering Analysis – Module D ")
    print("=" * 70)

    # Step 1: 运行模块 A / B / C
    run_results = run_modules()

    # Step 2: 收集交付物
    collected = collect_outputs(run_results)

    # Step 3: 生成聚合证据报告
    aggregated_report_path = generate_aggregated_report(collected)

    # Step 4: 调用 LLM 生成最终报告（可降级）
    if LLM_AVAILABLE:
        print("\n[Module D] Generating FINAL_REPORT.md using LLM...")
        try:
            _run_llm_stage(aggregated_report_path)
        except Exception as e:
            print("[WARN] LLM stage failed, falling back to evidence-only report")
            print(f"       Reason: {e}")
            _fallback_final_report(aggregated_report_path)
    else:
        print("\n[Module D] LLM not available, generating fallback report")
        _fallback_final_report(aggregated_report_path)

    print("\n[Module D] Pipeline completed successfully.")
    print(f"[Module D] Final report path: {FINAL_REPORT_PATH}")
    print("=" * 70)


# =========================
# LLM 相关
# =========================

def _run_llm_stage(aggregated_report_path: Path):
    """
    使用 LLM 生成 FINAL_REPORT.md
    """
    FINAL_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 1. 读取聚合报告内容作为上下文
    print(f"  -> Reading context from {aggregated_report_path.name}...")
    content = aggregated_report_path.read_text(encoding="utf-8")

    # 2. 调用 LLM 获取分析结果
    print("  -> Sending request to LLM (this may take a while)...")
    analysis_result = call_llm(content)

    # 3. 写入最终报告
    FINAL_REPORT_PATH.write_text(analysis_result, encoding="utf-8")
    print("  -> AI Analysis successfully written to FINAL_REPORT.md")


def _fallback_final_report(aggregated_report_path: Path):
    """
    LLM 不可用时的降级方案：
    直接复制 AGGREGATED_REPORT.md
    """
    FINAL_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    content = aggregated_report_path.read_text(encoding="utf-8")
    FINAL_REPORT_PATH.write_text(
        "# FINAL REPORT (Evidence Only)\n\n"
        "⚠️ 本报告未经过大模型综合解读，仅包含自动化聚合的证据内容。\n\n"
        + content,
        encoding="utf-8",
    )


# =========================
# CLI 入口
# =========================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Module D] 用户中断。")
        sys.exit(130)
