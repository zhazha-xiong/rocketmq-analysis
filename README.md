# rocketmq-analysis

用于课程作业的 Apache RocketMQ 仓库分析项目。

## 环境准备

在仓库根目录执行：

```bat
cd /d F:\workSpace\rocketmq-analysis

python -m venv .venv
.venv\Scripts\activate

python -m pip install -U pip
pip install -r requirements.txt
```

## 运行

### 模块B

1. **配置 Token**  
   首先需要[获取Github令牌](https://github.com/settings/tokens)（Classic Token，勾选 `repo` 权限即可）。  
   将 `scripts/module_b/.env.example` 复制为 `scripts/module_b/.env`，并将令牌填入：
   ```ini
   GITHUB_TOKEN=your_token_here
   ```

2. **一键运行**  
   该命令会自动执行：数据采集 -> 数据清洗 -> 图表生成。
   ```bat
   python scripts/module_b/main.py
   ```
   
   输出结果位于 `data/module_b/` 和 `figures/module_b/`。

### 模块C

1. **配置 Token**  
   首先需要[获取Github令牌](https://github.com/settings/tokens)（Classic Token，勾选 `repo` 权限即可）。  
   将 `scripts/module_c/.env.example` 复制为 `scripts/module_c/.env`，并将令牌填入：
   ```ini
   GITHUB_TOKEN=your_token_here
   ```

2. **一键运行**  
   该命令会自动执行：数据采集 -> 数据清洗 -> 图表生成 -> 报告生成。
   ```bat
   python scripts/module_c/main.py
   ```
   
   输出结果位于 `data/module_c/` 和 `figures/module_c/`。

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

