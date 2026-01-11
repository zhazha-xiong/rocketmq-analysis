# Github协作开发SOP

> Author：渣渣熊
> Date：2026/01/11

为了确保小组成员在代码贡献、分支管理、代码评审等环节拥有一致的协作标准，最大程度减少合并冲突、提高开发效率、保障代码质量，请所有小组成员严格按照此SOP完成大作业。

## 1 分支策略

- **main 分支**
  - `main` 是仓库的主干分支，必须始终保持干净、可用的状态。
  - 严禁直接向 `main` 分支提交任何代码。所有变更必须通过 Pull Request 合并。
- **特性分支 (Feature Branch)**
  - 所有新功能的开发、Bug 修复、文档撰写等任务，都必须从 `main` 分支创建新的特性分支。
  - 命名建议：采用 `类型/简短描述` 的格式，有助于快速识别分支用途。结合本次大作业模块，示例如下：
    - `feature/static-analysis`：开发代码静态分析模块
    - `feature/git-history`：开发 Git 提交历史分析模块
    - `feature/norm-assessment`：开发仓库规范性评估模块
    - `docs/update-readme`：更新 README 或报告文档
    - `fix/path-error`：修复脚本中的路径错误
- **Pull Request (PR) 合并策略**
  - 当特性分支的开发工作完成后，需向 `main` 分支发起一个 Pull Request。
  - 至少需要一名其他组员进行代码评审。
  - 评审通过后，由组长执行合并操作。
  - 建议使用 **Merge commit**（GitHub 按钮通常为 `Create a merge commit`），保留特性分支的提交历史与中间贡献者信息。

---

## 2 本地环境初始化

每位组员在项目开始时，需要进行一次本地环境的初始化配置。

### 2.1 统一 Git 用户信息
为了让 GitHub 正确识别你的代码贡献，请务必将本地 Git 的用户名和邮箱配置为与你的 GitHub 账号**完全一致**。

**全局配置：**
```bash
# 配置你的 GitHub 用户名
git config --global user.name "Your-GitHub-Username"

# 配置你的 GitHub 主邮箱
git config --global user.email "your-github-primary-email@example.com"
```

**项目配置：**
```bash
# 如只想对本仓库生效，可去掉 --global，在项目根目录执行
git config user.name "Your-GitHub-Username"
git config user.email "your-github-primary-email@example.com"
```

> 在 GitHub 个人设置的 Emails 页面可以找到你的主邮箱。请确保 user.email 与之匹配。

### 2.2 克隆仓库到本地

```bash
# 方式1 HTTPS
git clone https://github.com/zhazha-xiong/rocketmq-analysis.git
# 方式2 SSH
# 若使用 SSH，请先本地生成密钥并添加到 GitHub
git clone git@github.com:zhazha-xiong/rocketmq-analysis.git
```

### 2.3 进入项目目录并确认远程地址

克隆完成后，进入项目目录，并验证远程仓库地址是否正确配置。

```bash
# 进入项目目录
cd rocketmq-analysis

# 查看远程仓库地址，应能看到名为 origin 的远程仓库
git remote -v

输出应类似于：
origin  https://github.com/zhazha-xiong/rocketmq-analysis.git (fetch)
origin  https://github.com/zhazha-xiong/rocketmq-analysis.git (push)
```

---

## 3 日常开发流程

这是每位组员在开发新功能或修复问题时需要遵循的标准循环。

### 3.1 从远程更新本地 main 分支

在开始任何新任务之前，**务必确保你的本地 main 分支与远程仓库保持同步**。

```bash
# 首先切换到 main 分支
git checkout main

# 从远程仓库拉取最新的 main 分支内容
git pull origin main
```

### 3.2 创建新的特性分支

基于最新的 main 分支，创建一个新的特性分支。

```bash
# 创建并切换到新分支，例如开发 "静态分析" 功能
git checkout -b feature/static-analysis
```

### 3.3 本地开发与分批提交

在新创建的分支上进行开发工作。建议将一个大任务拆解为多个小的、逻辑独立的提交。
- **遵循“小步快跑”原则**：完成一个小的功能点或修复，就进行一次提交。
- **编写有意义的提交信息**：清晰地说明本次提交做了什么。

```bash
# 将相关文件添加到暂存区
git add src/static_analysis.py

# 提交你的修改，并附上清晰的提交信息
git commit -m "feat: 完成静态分析脚本骨架"
```

### 3.4 推送分支到远程仓库

当本地开发工作告一段落，或希望与他人分享进度时，**将你的特性分支推送到 GitHub**。

```bash
# -u 参数会自动将本地分支与远程同名分支关联起来，后续推送只需 git push
git push -u origin feature/static-analysis
```

### 3.5 发起 Pull Request

推送成功后，打开 GitHub 仓库页面，你会看到一个黄色的提示条，引导你为刚推送的分支创建一个 Pull Request。
1. **点击 Compare & pull request 按钮**。
2. **确认基准分支 (base) 为 main**，对比分支 (compare) 为你的特性分支。
3. **填写 PR 标题和描述**：
    - **标题**：清晰概括 PR 的目的，如 `feat: 实现代码静态分析模块`。
    - **描述**：详细说明你做了什么、解决了什么问题、如何测试，以及是否有需要特别注意的地方。
4. **指定评审人 (Reviewers)**：在右侧的 `Reviewers` 栏中，选择至少一名组员（或组长）来评审你的代码。
5. **点击 Create pull request**。

---

## 4 代码评审与合并

代码评审是保证质量、促进知识共享的关键环节。

### 4.1 评审要点

评审者应重点关注：

- **功能是否符合预期**：代码是否完成了 PR 描述中声称的功能？
- **代码可读性**：变量命名是否清晰？逻辑是否易于理解？是否有必要的注释？
- **风格是否一致**：是否遵循了团队约定的代码风格规范？
- **是否存在明显 Bug**：是否存在边界条件未处理、逻辑漏洞等问题？
- **是否影响现有功能**：修改是否对项目的其他部分产生了意料之外的副作用？

### 4.2 修改与讨论循环

1. 评审者在 PR 的 `Files changed` 页面对需要修改的代码行发表评论。
2. 开发者修复问题并推送到同一分支，PR 会自动更新。
3. 重复以上过程，直至所有问题都已解决。

```bash
# 根据评审意见修改代码...
git add .
git commit -m "fix: 根据评审意见优化静态分析逻辑"
git push
```

### 4.3 合并 PR 与清理分支

1. **当评审者认为代码没有问题后**，会点击 `Approve（批准）`。
2. **组长确认 PR 已被批准**，且所有自动化检查（如有）都已通过。
3. **组长点击 `Create a merge commit`（Merge Pull Request）按钮**，确认合并信息，完成合并。
4. 合并后，建议点击 `Delete branch` 删除远程特性分支，保持仓库整洁（代码已进入 `main`，删除分支不会丢失变更）。

合并后（本地同步 + 删除本地分支，可选）：

```bash
# 切换回 main 分支并拉取最新代码（包含刚刚合并的 PR）
git checkout main
git pull origin main

# 删除本地的特性分支
git branch -d feature/static-analysis
```

---

## 5 冲突避免与同步

在多人协作中，代码冲突是常见现象。遵循以下实践可以有效减少和解决冲突。

### 5.1 开始新任务前务必同步 main

在 `git checkout -b` 创建新分支之前，永远先同步 `main`：

```bash
git checkout main
git pull origin main
```

### 5.2 开发过程中与 main 保持同步

如果你的特性分支开发周期较长（例如超过一天），而 `main` 分支有新的代码合入，建议定期将 `main` 的最新变更同步到你的特性分支：

```bash
# 首先，确保本地 main 是最新的
git checkout main
git pull origin main

# 然后，切换回你的特性分支
git checkout feature/static-analysis

# 将最新的 main 分支合并到你的特性分支
git merge main
```

### 5.3 快速解决合并冲突

当 `git merge` 或 `git pull` 提示冲突 (Conflict) 时：

1. **打开冲突文件**：Git 会在冲突文件中用 `<<<<<<<`、`=======`、`>>>>>>>` 标记出不同分支的内容。
2. **手动编辑**：与组员讨论，决定保留哪部分代码，或如何将两部分代码合并；删除这些标记。
3. **完成合并**：

```bash
# 在解决所有文件的所有冲突后，将它们标记为已解决
git add .

# 执行提交
git commit -m "fix: 合并 main 分支并解决冲突"
```

---

## 6 提交信息与分支命名规范

一致的命名规范极大地提升了项目的可维护性。

### 6.1 提交信息 (Commit Message)

建议采用 `类型: 描述` 的格式。

- `feat:` 新增功能
- `fix:` 修复 Bug
- `docs:` 修改文档
- `style:` 代码格式修改（不影响代码逻辑）
- `refactor:` 代码重构
- `test:` 增加或修改测试
- `chore:` 构建过程或辅助工具的变动

示例：

- `feat: 添加静态分析主脚本`
- `fix: 修复 git 历史解析脚本的日期处理错误`
- `docs: 更新大作业报告的需求分析章节`

### 6.2 分支命名 (Branch Name)

建议采用 `类型/简短描述` 的格式，分支名应反映其目的。分支名统一小写，连字符分隔。

示例：

- `feature/static-analysis`
- `feature/git-history`
- `feature/norm-assessment`
- `docs/update-readme`
- `fix/path-error`