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

首先需要[获取Github令牌](https://github.com/settings/tokens)
然后将令牌填入`.env`中：`GITHUB_TOKEN=<GITHUB_TOKEN>`

[参考文档](https://docs.github.com/zh/rest/commits/commits?apiVersion=2022-11-28)

