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

### 模块B：研发效能与工作节律

```bat
python -m scripts.module_b
```

#### 产物输出位置

- 数据：`data/module_b/<repo_name>/...`
- 图表：`figures/module_b/<repo_name>/...`

#### 运行测试

```bat
.venv\Scripts\activate
pytest -q
```

