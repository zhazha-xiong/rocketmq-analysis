import os
import json
from datetime import datetime

def load_data(json_path):
    if not os.path.exists(json_path):
        raise RuntimeError(f"数据文件缺失: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_markdown(data, output_path):
    total_score = data['total_score']
    
    grade = "D"
    if total_score >= 90: grade = "S"
    elif total_score >= 80: grade = "A"
    elif total_score >= 70: grade = "B"
    elif total_score >= 60: grade = "C"
    
    md_content = f"""# RocketMQ 仓库规范性评估报告 (Module C)

> **生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
> **评估对象**: Apache RocketMQ (GitHub)

## 1. 评估综述

| 综合得分 | 评级 | 评估概览 |
| :---: | :---: | :--- |
| **{total_score}** / 100 | **{grade}** | 本次评估基于社区四大核心维度：版本控制、持续集成、社区治理、代码质量。 |

### 能力雷达图
![Radar Chart](../../figures/module_c/radar_chart.png)

---

## 2. 维度详细得分

![Breakdown Chart](../../figures/module_c/breakdown_chart.png)

### 2.1 版本控制 (Version Control)
**得分**: {data['version_control']['total']} / 25.0

*   **Commit 规范性**: {data['version_control']['commit_norm']:.2f} / 15.0
    *   *说明*: 检查提交信息是否符合 Conventional Commits (如 `feat:`, `fix:`) 或 Apache issue 格式 (`[ISSUE #123]`)。
*   **PR 流程规范**: {data['version_control']['pr_process']:.2f} / 10.0
    *   *说明*: 检查 PR 是否包含详细描述(Body)、是否指定了 Reviewer 或 Label。

### 2.2 持续集成 (CI Health)
**得分**: {data['ci_health']['total']} / 20.0

*   **CI 运行成功率**: {data['ci_health']['run_rate']:.2f} / 15.0
    *   *统计*: 成功/总数 = {data['ci_health']['stats']} (已过滤 Cancelled 状态)
*   **CI 配置文件**: {data['ci_health']['config_exist']:.2f} / 5.0
    *   *说明*: 检查 `.github/workflows` 目录及其内容。

### 2.3 社区治理 (Governance)
**得分**: {data['governance']['total']} / 30.0

*   **关键文档完备性**: {data['governance']['docs']:.2f} / 15.0
    *   *说明*: 检查 README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT 等文件。
*   **版本发布周期**: {data['governance']['release_cycle']:.2f} / 15.0
    *   *说明*: 基于最近 10 个版本的发布时间间隔计算。

### 2.4 代码质量 (Code Quality)
**得分**: {data['code_quality']['total']} / 25.0

*   **测试框架配置**: {data['code_quality']['test_config']:.2f} / 10.0
    *   *说明*: 检查 `pom.xml` 中是否存在 JUnit/Mockito/JaCoCo 等依赖。
*   **代码规范配置**: {data['code_quality']['style_config']:.2f} / 15.0
    *   *说明*: 检查 Checkstyle/Spotless 等代码风格检查插件的配置。

---

## 3. 改进建议

"""
    if data['version_control']['commit_norm'] < 10:
        md_content += "- **版本控制**: 建议在 `CONTRIBUTING.md` 中加强对 Commit Message 格式的要求，或引入 `commitlint` 工具。\n"
    if data['ci_health']['run_rate'] < 10:
        md_content += "- **持续集成**: CI 失败率较高，建议排查不稳定测试用例 (Flaky Tests) 或环境配置问题。\n"
    if data['governance']['docs'] < 15:
        md_content += "- **社区治理**:缺少部分关键社区文档（如行为准则或贡献指南），完善这些文档有助于降低贡献门槛。\n"
    if data['code_quality']['style_config'] < 10:
        md_content += "- **代码质量**: 未检测到强制的代码风格检查工具，建议引入 Maven Checkstyle Plugin 并配置 CI 门禁。\n"

    if "建议" not in md_content[-10:]:
        md_content += "- 项目在各项指标上表现良好，请继续保持。\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"[OK] 报告已生成: {output_path}")

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(current_dir))
    
    json_path = os.path.join(repo_root, "data", "module_c", "clean_scores.json")
    report_path = os.path.join(repo_root, "data", "module_c", "REPORT.md")
    
    try:
        data = load_data(json_path)
        generate_markdown(data, report_path)
    except Exception as e:
        print(f"[Error] 报告生成失败: {str(e)}")

if __name__ == "__main__":
    main()