# rocketmq-analysis

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)

> 开源软件基础 Apache RocketMQ 仓库综合分析工具

---

## 简介

本项目以 Apache RocketMQ 仓库为例，提供一套可复用的分析流水线，用于从 GitHub 采集数据、清洗派生指标、生成图表并输出 Markdown 报告。

当前包含的分析模块（均在 `scripts/` 下）：

- 模块A：代码静态分析
- 模块B：提交历史分析
- 模块C：仓库规范性评估
- 模块D：智能化汇总

A、B、C模块运行后会在对应目录生成：

- `data/module_x/`：原始数据、清洗结果与 `REPORT.md`
- `figures/module_x/`：可视化图表

D模块为整个程序的统一运行入口，运行后会在对应目录生成：

- `data/module_d/AGGREGATED_REPORT.md`：模块ABC的输出生成聚合报告
- `docs/FINAL_REPORT.md`：AI分析报告

**目录结构**：

```text
rocketmq-analysis
├── data
│   ├── module_a
│   ├── module_b
│   ├── module_c
│   └── module_d
├── figures
│   ├── module_a
│   ├── module_b
│   └── module_c
├── scripts
│   ├── module_a
│   ├── module_b
│   ├── module_c
│   └── module_d 
├── examples
├── tests
└── docs

```

---

## 环境准备

要求：Python 3.10+

在项目根目录执行：

```bat
python -m venv .venv
.venv\Scripts\activate

python -m pip install -U pip
pip install -r requirements.txt
```

## 单元测试

在项目根目录执行：

```bat
.venv\Scripts\python.exe -m pytest -q
```

## 运行

**配置 Token**

首先需要[获取Github令牌](https://github.com/settings/tokens)（Classic Token，勾选 `repo` 权限即可）。
  将 `scripts/.env.example` 复制为 `scripts/.env`，并将令牌填入：

```ini
   GITHUB_TOKEN=your_token_here
```

**配置LLM API**

获取需要使用的LLM的API、URL及MODEL_NAME，推荐[火山方舟](https://www.volcengine.com/product/ark)以及[阿里云](https://www.aliyun.com/)平台

成功获取后在`scripts/.env`填入：

```ini
   LLM_API_KEY=your_api_here
   LLM_BASE_URL=your_base_url_here
   LLM_MODEL_NAME=your_model_name_here
```

**前置仓库准备**

需要先克隆目标Python客户端仓库到 `temp_repos/` 目录，请在项目根目录下运行以下代码：

```bat
   mkdir temp_repos
   cd temp_repos
   git clone https://github.com/apache/rocketmq-client-python.git
   git clone https://github.com/apache/rocketmq-clients.git
   cd ..
```

**一键运行**

请在项目根目录下运行以下代码，该命令会自动执行：模块A -> 模块B -> 模块C -> 整合报告生成 -> AI分析报告生成。

```bat
   python scripts/module_d/main.py
```

   输出结果位于 `data/module_d/AGGREGATED_REPORT.md` 和 `docs/FINAL_REPORT.md`。

**示例**

本项目提供了最终结果的示例文件，文件为位于`examples/`下的`demo_result.pdf`。

## 评分规则

### 模块C

**评分规则说明 (满分 100 分)**

该模块通过 `scripts/module_c/clean_git_data.py` 根据采集的数据自动计算项目健康度得分。

1. **版本控制 - 25分**

   - **Commit 规范 (15分)**:
     - 规则: 检查 Commit Message 是否符合 Conventional Commits 规范 (如 `feat:`, `fix:`) 或 Apache 社区 Issue 格式 (`[ISSUE #123]`).
     - 计算: `(规范 Commit 数 / 总 Commit 数) * 15`
   - **PR 流程规范 (10分)**:
     - 规则: PR 必须包含详细描述 (Body > 10字符) 或 包含元数据 (Assignee / Reviewers / Labels).
     - 计算: `(合规 PR 数 / 总 PR 数) * 10`
2. **持续集成 - 20分**

   - **运行成功率 (15分)**:
     - 规则: 计算最近 Workflow 运行的成功率 (排除 Cancelled/Skipped 状态).
     - 计算: `(Success / Effective Runs) * 15`
   - **CI 配置 (5分)**:
     - 规则: 检查是否存在 `.github/workflows` 目录.
3. **社区治理 - 30分**

   - **文档完备性 (15分)**:
     - 规则: 检查 `LICENSE`, `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
     - 计算: 每存在一个文件得 3.75 分.
   - **发布周期 (15分)**:
     - 规则: 计算最近 10 个版本的平均发布间隔.
     - 计算: 间隔 <= 90 天得满分，超过则按每 10 天扣 1 分递减.
4. **代码质量 - 25分**

   - **测试配置 (10分)**:
     - 规则: 检查是否存在测试配置 (如 `pom.xml`).
   - **代码规范 (15分)**:
     - 规则: 检查是否存在代码风格配置 (如 `.editorconfig`) 或在 `pom.xml` 中配置了 `maven-checkstyle-plugin`/`spotless-maven-plugin`.
