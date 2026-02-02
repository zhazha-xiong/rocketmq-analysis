"""
测试模块 D 的收集器 (collector.py)
"""
import sys
from pathlib import Path
import pytest

# 添加 scripts 目录到路径，以便导入 module_d
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "scripts"))
# 添加 scripts/module_d 目录到路径，以便 collector.py 能找到同级 utils
sys.path.insert(0, str(repo_root / "scripts" / "module_d"))

from module_d import collector

@pytest.fixture
def mock_workspace(tmp_path):
    """
    创建一个伪造的工作区结构，包含 data 和 figures 目录
    """
    data_dir = tmp_path / "data"
    figures_dir = tmp_path / "figures"
    
    for module in ["module_a", "module_b", "module_c"]:
        (data_dir / module).mkdir(parents=True, exist_ok=True)
        (figures_dir / module).mkdir(parents=True, exist_ok=True)
        
    return {
        "root": tmp_path,
        "data": data_dir,
        "figures": figures_dir
    }

@pytest.fixture
def patched_modules(mock_workspace, monkeypatch):
    """
    Patch collector.MODULES to point to the temporary directory
    """
    data = mock_workspace["data"]
    figures = mock_workspace["figures"]
    
    new_modules = {
        "module_a": {
            "report": data / "module_a/REPORT.md",
            "figures": figures / "module_a",
        },
        "module_b": {
            "report": data / "module_b/REPORT.md",
            "figures": figures / "module_b",
        },
        "module_c": {
            "report": data / "module_c/REPORT.md",
            "figures": figures / "module_c",
        },
    }
    
    monkeypatch.setattr(collector, "MODULES", new_modules)
    return new_modules

def test_collect_outputs_happy_path(mock_workspace, patched_modules):
    """
    测试所有文件都存在且正常的完美情况
    """
    data = mock_workspace["data"]
    figures = mock_workspace["figures"]
    
    # 准备文件
    for module in ["module_a", "module_b", "module_c"]:
        # 创建非空报告
        (data / module / "REPORT.md").write_text("Report Content")
        # 创建图片
        (figures / module / "figure1.png").touch()
        (figures / module / "figure2.png").touch()

    # 模拟 runner 结果
    run_results = {
        "module_a": {"executed": True, "success": True, "exit_code": 0},
        "module_b": {"executed": True, "success": True, "exit_code": 0},
        "module_c": {"executed": True, "success": True, "exit_code": 0},
    }

    # 执行收集
    collected = collector.collect_outputs(run_results)

    # 验证
    for module in ["module_a", "module_b", "module_c"]:
        assert module in collected
        res = collected[module]
        assert res["executed"] is True
        assert res["success"] is True
        assert res["report_exists"] is True
        assert res["figures_count"] == 2
        assert len(res["issues"]) == 0
        assert str(data / module / "REPORT.md") == res["report_path"]
        assert any("figure1.png" in f for f in res["figures"])

def test_collect_outputs_missing_report(mock_workspace, patched_modules):
    """
    测试报告缺失的情况
    """
    # 仅创建 module_a 的报告
    (mock_workspace["data"] / "module_a/REPORT.md").write_text("Content")
    
    # module_b 不创建报告 (missing)
    
    run_results = {
        "module_a": {"executed": True, "success": True},
        "module_b": {"executed": True, "success": True},
    }
    
    collected = collector.collect_outputs(run_results)
    
    # module_a 正常
    assert collected["module_a"]["report_exists"] is True
    assert "REPORT.md missing" not in collected["module_a"]["issues"]

    # module_b 报告缺失
    assert collected["module_b"]["report_exists"] is False
    assert "REPORT.md missing" in collected["module_b"]["issues"]

def test_collect_outputs_empty_report(mock_workspace, patched_modules):
    """
    测试报告存在但为空的情况
    """
    # 创建空文件
    (mock_workspace["data"] / "module_a/REPORT.md").touch()
    
    run_results = {"module_a": {"executed": True, "success": True}}
    
    collected = collector.collect_outputs(run_results)
    
    assert collected["module_a"]["report_exists"] is True
    assert "REPORT.md is empty" in collected["module_a"]["issues"]

def test_collect_outputs_no_figures(mock_workspace, patched_modules):
    """
    测试没有图片的情况
    """
    (mock_workspace["data"] / "module_a/REPORT.md").write_text("Content")
    # figures 目录存在但为空
    
    run_results = {"module_a": {"executed": True, "success": True}}
    
    collected = collector.collect_outputs(run_results)
    
    assert collected["module_a"]["figures_count"] == 0
    assert "No figures found" in collected["module_a"]["issues"]

def test_collect_figures_helper(mock_workspace, patched_modules):
    """
    单独测试 _collect_figures 辅助函数
    """
    fig_dir = mock_workspace["figures"] / "module_test"
    fig_dir.mkdir()
    
    (fig_dir / "a.png").touch()
    (fig_dir / "b.png").touch()
    (fig_dir / "c.txt").touch() # 不应被收集
    
    figs = collector._collect_figures(fig_dir)
    assert len(figs) == 2
    assert any("a.png" in f for f in figs)
    assert not any("c.txt" in f for f in figs)

def test_collect_figures_nonexistent_dir(tmp_path):
    """
    测试不存在的图片目录
    """
    path = tmp_path / "nonexistent"
    figs = collector._collect_figures(path)
    assert figs == []
