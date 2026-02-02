"""
测试模块A的报告生成器
"""
import os
import sys
from pathlib import Path

import pandas as pd
import pytest

# 添加 scripts 目录到路径
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "scripts"))

from module_a import report_generator


def test_safe_pct():
    """测试百分比计算"""
    assert report_generator._safe_pct(25, 100) == 25.0
    assert abs(report_generator._safe_pct(1, 3) - 33.333333) < 0.001
    assert report_generator._safe_pct(0, 100) == 0.0
    assert report_generator._safe_pct(10, 0) == 0.0  # 分母为0


def test_md_table():
    """测试Markdown表格生成"""
    rows = [
        ("仓库", "文件数"),
        ("rocketmq-client-python", "42"),
        ("rocketmq-clients", "138")
    ]
    result = report_generator._md_table(rows)
    
    assert "| 仓库 | 文件数 |" in result
    assert "| --- | --- |" in result
    assert "| rocketmq-client-python | 42 |" in result
    assert "| rocketmq-clients | 138 |" in result


def test_load_data_missing_files(tmp_path):
    """测试加载不存在的文件"""
    fake_path = tmp_path / "nonexistent.csv"
    
    with pytest.raises(RuntimeError, match="文件扫描数据不存在|Bandit扫描结果不存在|Lizard分析结果不存在"):
        report_generator.load_data(
            str(fake_path),
            str(fake_path),
            str(fake_path)
        )


def test_build_markdown_empty_data(tmp_path):
    """测试空数据时的报告生成"""
    # 创建空的DataFrames
    df_files = pd.DataFrame(columns=["repository", "file_path"])
    df_bandit = pd.DataFrame(columns=["repository", "file_path", "issue_severity"])
    df_lizard = pd.DataFrame(columns=["repository", "file_path", "nloc", "ccn", "param"])
    
    markdown = report_generator.build_markdown(
        df_files, df_bandit, df_lizard,
        figures_rel_dir="../../figures/module_a"
    )
    
    # 检查基本结构
    assert "## 1. 分析范围" in markdown
    assert "## 2. 关键结论" in markdown
    assert "## 3. 图表与解读" in markdown
    assert "## 4. 局限性与改进方向" in markdown
    
    # 空数据应该显示0
    assert "共扫描 **0** 个Python文件" in markdown or "扫描Python文件总数 | 0" in markdown


def test_build_markdown_with_data():
    """测试包含数据时的报告生成"""
    # 创建测试数据
    df_files = pd.DataFrame({
        "repository": ["rocketmq-client-python", "rocketmq-clients"],
        "file_path": ["src/main.py", "src/test.py"]
    })
    
    df_bandit = pd.DataFrame({
        "repository": ["rocketmq-client-python"],
        "file_path": ["src/main.py"],
        "issue_severity": ["MEDIUM"]
    })
    
    df_lizard = pd.DataFrame({
        "repository": ["rocketmq-client-python", "rocketmq-clients"],
        "file_path": ["src/main.py", "src/test.py"],
        "nloc": [100, 50],
        "ccn": [5, 3],
        "param": [2, 1]
    })
    
    markdown = report_generator.build_markdown(
        df_files, df_bandit, df_lizard,
        figures_rel_dir="../../figures/module_a"
    )
    
    # 检查数据被包含
    assert "共扫描 **2** 个Python文件" in markdown or "扫描Python文件总数 | 2" in markdown
    assert "rocketmq-client-python" in markdown


def test_build_markdown_includes_all_figure_paths():
    """测试报告包含所有必需的图表路径"""
    # 创建最小测试数据
    df_files = pd.DataFrame({"repository": ["test"], "file_path": ["test.py"]})
    df_bandit = pd.DataFrame({"repository": ["test"], "file_path": ["test.py"], "issue_severity": ["HIGH"]})
    df_lizard = pd.DataFrame({
        "repository": ["test"],
        "file_path": ["test.py"],
        "nloc": [100],
        "ccn": [5],
        "param": [2]
    })
    
    markdown = report_generator.build_markdown(
        df_files, df_bandit, df_lizard,
        figures_rel_dir="../../figures/module_a"
    )
    
    # 检查5个图表路径
    expected_figures = [
        "../../figures/module_a/bandit_severity_distribution.png",
        "../../figures/module_a/bandit_top_issues.png",
        "../../figures/module_a/complexity_distribution.png",
        "../../figures/module_a/top_complex_functions.png",
        "../../figures/module_a/repository_comparison.png"
    ]
    
    for fig_path in expected_figures:
        assert fig_path in markdown, f"缺失图表路径: {fig_path}"


def test_build_markdown_quantitative_conclusions():
    """测试报告包含定量结论"""
    df_files = pd.DataFrame({
        "repository": ["repo1", "repo2"],
        "file_path": ["a.py", "b.py"]
    })
    
    df_bandit = pd.DataFrame({
        "repository": ["repo1"],
        "file_path": ["a.py"],
        "issue_severity": ["HIGH"]
    })
    
    df_lizard = pd.DataFrame({
        "repository": ["repo1", "repo2"],
        "file_path": ["a.py", "b.py"],
        "nloc": [200, 100],
        "ccn": [15, 5],
        "param": [3, 2]
    })
    
    markdown = report_generator.build_markdown(
        df_files, df_bandit, df_lizard,
        figures_rel_dir="../../figures/module_a"
    )
    
    # 检查是否包含数字和百分比
    import re
    has_numbers = bool(re.search(r'\d+', markdown))
    has_percentage = bool(re.search(r'\d+\.\d+%|\d+%', markdown))
    
    assert has_numbers, "报告应包含数字统计"
    assert has_percentage or "扫描文件数: **2**" in markdown, "报告应包含百分比或具体数字"
