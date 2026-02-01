import os
import sys
import json

scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from report_utils import get_repo_root, now_str, write_text  # noqa: E402

def load_data(json_path: str) -> dict:
    if not os.path.exists(json_path):
        raise RuntimeError(f"数据文件缺失: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_markdown(data: dict, *, figures_rel_dir: str) -> str:
    total_score = data["total_score"]
    
    grade = "D"
    if total_score >= 90:
        grade = "S"
    elif total_score >= 80:
        grade = "A"
    elif total_score >= 70:
        grade = "B"
    elif total_score >= 60:
        grade = "C"

    fig = lambda filename: f"{figures_rel_dir}/{filename}"

    lines: list[str] = [
        "# RocketMQ 仓库规范性评估报告 (Module C)",
        "",
        f"生成时间：{now_str()}",
        "评估对象：Apache RocketMQ (GitHub)",
        "",
        "## 1. 评估综述",
        "",
        "| 综合得分 | 评级 | 评估概览 |",
        "| :---: | :---: | :--- |",
        f"| **{total_score}** / 100 | **{grade}** | 本次评估基于社区四大核心维度：版本控制、持续集成、社区治理、代码质量。 |",
        "",
        "### 能力雷达图",
        f"![能力雷达图]({fig('radar_chart.png')})",
        "",
        "---",
        "",
        "## 2. 维度详细得分",
        "",
        f"![细分指标图]({fig('breakdown_chart.png')})",
        "",
        "### 2.1 版本控制 (Version Control)",
        f"**得分**: {data['version_control']['total']} / 25.0",
        "",
        f"- **Commit 规范性**: {data['version_control']['commit_norm']:.2f} / 15.0",
        "  - 说明：检查提交信息是否符合 Conventional Commits（如 `feat:`, `fix:`）或 Apache issue 格式（`[ISSUE #123]`）。",
        f"- **PR 流程规范**: {data['version_control']['pr_process']:.2f} / 10.0",
        "  - 说明：检查 PR 是否包含详细描述（Body）、是否指定 Reviewer 或 Label。",
        "",
        "### 2.2 持续集成 (CI Health)",
        f"**得分**: {data['ci_health']['total']} / 20.0",
        "",
        f"- **CI 运行成功率**: {data['ci_health']['run_rate']:.2f} / 15.0",
        f"  - 统计：成功/总数 = {data['ci_health']['stats']}（已过滤 Cancelled 状态）",
        f"- **CI 配置文件**: {data['ci_health']['config_exist']:.2f} / 5.0",
        "  - 说明：检查 `.github/workflows` 目录及其内容。",
        "",
        "### 2.3 社区治理 (Governance)",
        f"**得分**: {data['governance']['total']} / 30.0",
        "",
        f"- **关键文档完备性**: {data['governance']['docs']:.2f} / 15.0",
        "  - 说明：检查 README、LICENSE、CONTRIBUTING、CODE_OF_CONDUCT 等文件。",
        f"- **版本发布周期**: {data['governance']['release_cycle']:.2f} / 15.0",
        "  - 说明：基于最近 10 个版本的发布时间间隔计算。",
        "",
        "### 2.4 代码质量 (Code Quality)",
        f"**得分**: {data['code_quality']['total']} / 25.0",
        "",
        f"- **测试框架配置**: {data['code_quality']['test_config']:.2f} / 10.0",
        "  - 说明：检查 `pom.xml` 中是否存在 JUnit/Mockito/JaCoCo 等依赖。",
        f"- **代码规范配置**: {data['code_quality']['style_config']:.2f} / 15.0",
        "  - 说明：检查 Checkstyle/Spotless 等代码风格检查插件的配置。",
        "",
        "---",
        "",
        "## 3. 改进建议",
        "",
    ]

    suggestions: list[str] = []
    if data["version_control"]["commit_norm"] < 10:
        suggestions.append("- **版本控制**：建议在 `CONTRIBUTING.md` 中加强对 Commit Message 格式的要求，或引入 `commitlint` 工具。")
    if data["ci_health"]["run_rate"] < 10:
        suggestions.append("- **持续集成**：CI 失败率较高，建议排查不稳定测试用例（Flaky Tests）或环境配置问题。")
    if data["governance"]["docs"] < 15:
        suggestions.append("- **社区治理**：缺少部分关键社区文档（如行为准则或贡献指南），完善这些文档有助于降低贡献门槛。")
    if data["code_quality"]["style_config"] < 10:
        suggestions.append("- **代码质量**：未检测到强制的代码风格检查工具，建议引入 Maven Checkstyle Plugin 并配置 CI 门禁。")

    if not suggestions:
        suggestions.append("- 项目在各项指标上表现良好，请继续保持。")

    lines.extend(suggestions)
    return "\n".join(lines) + "\n"

def main() -> None:
    repo_root = get_repo_root(__file__)
    json_path = os.path.join(repo_root, "data", "module_c", "clean_scores.json")
    report_path = os.path.join(repo_root, "data", "module_c", "REPORT.md")

    figures_rel_dir = "../../figures/module_c"

    data = load_data(json_path)
    md = build_markdown(data, figures_rel_dir=figures_rel_dir)
    write_text(report_path, md)
    print(f"[OK] 模块 C 子报告已生成: {report_path}")

if __name__ == "__main__":
    main()