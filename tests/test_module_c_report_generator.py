import os
import sys

import pytest


def _ensure_scripts_on_path():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scripts_dir = os.path.join(repo_root, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)


_ensure_scripts_on_path()

from module_c import report_generator


def test_load_data_missing_file_raises(tmp_path):
    missing = tmp_path / "not_exists.json"
    with pytest.raises(RuntimeError):
        report_generator.load_data(str(missing))


@pytest.mark.parametrize(
    "score,expected_grade",
    [
        (95, "S"),
        (85, "A"),
        (75, "B"),
        (65, "C"),
        (50, "D"),
    ],
)
def test_build_markdown_grade_mapping(monkeypatch, score, expected_grade):
    monkeypatch.setattr(report_generator, "now_str", lambda: "2026-02-01 00:00:00")

    data = {
        "total_score": score,
        "version_control": {"total": 0, "commit_norm": 0, "pr_process": 0},
        "ci_health": {"total": 0, "run_rate": 0, "config_exist": 0, "stats": "0/0"},
        "governance": {"total": 0, "docs": 0, "release_cycle": 0},
        "code_quality": {"total": 0, "test_config": 0, "style_config": 0},
    }

    md = report_generator.build_markdown(data, figures_rel_dir="../../figures/module_c")
    assert f"| **{score}** / 100 | **{expected_grade}** |" in md


def test_build_markdown_includes_figure_paths_and_suggestions(monkeypatch):
    monkeypatch.setattr(report_generator, "now_str", lambda: "2026-02-01 00:00:00")

    data = {
        "total_score": 55,
        "version_control": {"total": 5, "commit_norm": 5, "pr_process": 0},
        "ci_health": {"total": 5, "run_rate": 5, "config_exist": 0, "stats": "1/2"},
        "governance": {"total": 10, "docs": 0, "release_cycle": 10},
        "code_quality": {"total": 5, "test_config": 0, "style_config": 5},
    }

    md = report_generator.build_markdown(data, figures_rel_dir="../../figures/module_c")

    assert "生成时间：2026-02-01 00:00:00" in md
    assert "评估对象：Apache RocketMQ (GitHub)" in md

    assert "../../figures/module_c/radar_chart.png" in md
    assert "../../figures/module_c/breakdown_chart.png" in md

    assert "- **版本控制**" in md
    assert "- **持续集成**" in md
    assert "- **社区治理**" in md
    assert "- **代码质量**" in md
