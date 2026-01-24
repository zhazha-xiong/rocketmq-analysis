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

