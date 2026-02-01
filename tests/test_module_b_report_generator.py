import os
import sys

import pandas as pd
from module_b import report_generator

def _import_report_generator():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scripts_dir = os.path.join(repo_root, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    return report_generator


def test_safe_pct():
    rg = _import_report_generator()
    assert rg._safe_pct(1, 2) == 50.0
    assert rg._safe_pct(1, 0) == 0.0


def test_md_table():
    rg = _import_report_generator()
    table = rg._md_table([("a", "1"), ("b", "2")])
    assert "| 指标 | 值 |" in table
    assert "| a | 1 |" in table
    assert "| b | 2 |" in table


def test_load_data_computes_overtime(monkeypatch, tmp_path):
    rg = _import_report_generator()

    monkeypatch.setattr(rg, "is_workday", lambda d: True)

    clean_csv = tmp_path / "clean_commits.csv"
    pd.DataFrame(
        [
            {"time": "2026-02-01 09:00:00", "name": "alice"},
            {"time": "2026-02-01 10:00:00", "name": "bob"},
            {"time": "2026-02-01 19:00:00", "name": "carol"},
        ]
    ).to_csv(clean_csv, index=False)

    df = rg.load_data(str(clean_csv))

    assert set(["hour", "weekday", "date", "is_workday", "is_overtime"]).issubset(df.columns)
    assert bool(df.loc[df["name"] == "alice", "is_overtime"].iloc[0]) is True  # 09:00
    assert bool(df.loc[df["name"] == "bob", "is_overtime"].iloc[0]) is False  # 10:00
    assert bool(df.loc[df["name"] == "carol", "is_overtime"].iloc[0]) is True  # 19:00


def test_build_markdown_empty(monkeypatch):
    rg = _import_report_generator()
    monkeypatch.setattr(rg, "now_str", lambda: "2026-02-01 00:00:00")

    md = rg.build_markdown(pd.DataFrame(), figures_rel_dir="../../figures/module_b")
    assert "生成时间：2026-02-01 00:00:00" in md
    assert "评估对象：Apache RocketMQ (GitHub)" in md
    assert "数据不足" in md


def test_build_markdown_includes_figure_paths(monkeypatch):
    rg = _import_report_generator()
    monkeypatch.setattr(rg, "now_str", lambda: "2026-02-01 00:00:00")

    df = pd.DataFrame(
        {
            "time": pd.to_datetime(["2026-02-01 10:00:00", "2026-02-02 20:00:00"]),
            "name": ["alice", "alice"],
            "hour": [10, 20],
            "weekday": [5, 0],
            "date": [pd.Timestamp("2026-02-01").date(), pd.Timestamp("2026-02-02").date()],
            "is_workday": [True, True],
            "is_overtime": [False, True],
        }
    )

    md = rg.build_markdown(df, figures_rel_dir="../../figures/module_b")
    assert "../../figures/module_b/overtime_holiday_pie.png" in md
    assert "../../figures/module_b/commit_heatmap.png" in md
