import os
from datetime import datetime
from typing import Iterable

import pandas as pd
from chinese_calendar import is_workday


def _safe_pct(numerator: int, denominator: int) -> float:
    return (numerator / denominator * 100.0) if denominator else 0.0


def _fmt_dt(dt: pd.Timestamp | None) -> str:
    if dt is None or pd.isna(dt):
        return "-"
    if isinstance(dt, pd.Timestamp):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)


def _md_table(rows: Iterable[tuple[str, str]]) -> str:
    lines = ["| 指标 | 值 |", "| --- | --- |"]
    for k, v in rows:
        lines.append(f"| {k} | {v} |")
    return "\n".join(lines)


def load_and_enrich_clean_commits(clean_csv_path: str) -> pd.DataFrame:
    if not os.path.exists(clean_csv_path):
        raise RuntimeError(f"清洗后的提交数据不存在: {clean_csv_path}，请先运行模块 B 的数据采集与清洗")

    df = pd.read_csv(clean_csv_path)
    if df.empty:
        return df

    if "time" not in df.columns or "name" not in df.columns:
        raise RuntimeError(f"clean_commits.csv 字段不符合预期，需要包含 time/name: {clean_csv_path}")

    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna(subset=["time"])

    df["hour"] = df["time"].dt.hour
    df["weekday"] = df["time"].dt.dayofweek
    df["date"] = df["time"].dt.date

    unique_dates = df["date"].unique()
    workday_map = {d: is_workday(d) for d in unique_dates}
    df["is_workday"] = df["date"].map(workday_map)

    df["is_overtime"] = (~df["is_workday"]) | (
        (df["is_workday"]) & ((df["hour"] < 10) | (df["hour"] >= 19))
    )

    return df


def generate_report(df: pd.DataFrame, *, figures_rel_dir: str) -> str:
    now_str = datetime.now().strftime("%Y-%m-%d")

    if df.empty:
        return (
            "# 模块 B：研发效能与工作节律（提交历史）\n\n"
            f"生成日期：{now_str}\n\n"
            "## 1. 分析范围\n"
            "- 仓库：`apache/rocketmq`\n"
            "- 数据源：GitHub REST API（Commits API）\n"
            "- 说明：当前未获得有效提交样本（clean_commits.csv 为空或时间字段解析失败）\n\n"
            "## 2. 关键结论\n"
            "- 数据不足，无法得出稳定结论。\n\n"
            "## 3. 图表与解读\n"
            "- 数据不足，未生成图表或图表不可用。\n\n"
            "## 4. 局限性\n"
            "- 可能受到 API 限速、网络错误或采集时间窗口影响。\n"
        )

    total_commits = int(len(df))
    start_time = df["time"].min() if total_commits else None
    end_time = df["time"].max() if total_commits else None

    unique_authors = int(df["name"].fillna("").replace("", pd.NA).dropna().nunique())

    holiday_commits = int((~df["is_workday"]).sum())
    holiday_pct = _safe_pct(holiday_commits, total_commits)

    overtime_commits = int(df["is_overtime"].sum())
    overtime_pct = _safe_pct(overtime_commits, total_commits)

    workday_df = df[df["is_workday"]].copy()
    workday_total = int(len(workday_df))
    workday_overtime_commits = int(((workday_df["hour"] < 10) | (workday_df["hour"] >= 19)).sum())
    workday_overtime_pct = _safe_pct(workday_overtime_commits, workday_total)

    top_authors = (
        df.dropna(subset=["name"])
        .assign(name=df["name"].astype(str).str.strip())
        .query("name != ''")
        .groupby("name")
        .size()
        .sort_values(ascending=False)
        .head(10)
    )

    metrics = _md_table(
        [
            ("样本提交数", str(total_commits)),
            ("贡献者数量（按 name 去重）", str(unique_authors)),
            ("样本时间范围（北京时间）", f"{_fmt_dt(start_time)} ~ {_fmt_dt(end_time)}"),
            ("节假日/周末提交占比", f"{holiday_commits}（{holiday_pct:.1f}%）"),
            ("加班提交占比（节假日/周末 + 工作日非核心时段）", f"{overtime_commits}（{overtime_pct:.1f}%）"),
            ("工作日加班占比（<10:00 或 >=19:00）", f"{workday_overtime_commits}（{workday_overtime_pct:.1f}%）"),
        ]
    )

    if top_authors.empty:
        top_authors_md = "- 无法统计贡献者排名（name 字段为空）。"
    else:
        lines = ["| 排名 | 贡献者（name） | 提交数 |", "| --- | --- | --- |"]
        for i, (name, cnt) in enumerate(top_authors.items(), start=1):
            lines.append(f"| {i} | {name} | {int(cnt)} |")
        top_authors_md = "\n".join(lines)

    fig = lambda filename: f"{figures_rel_dir}/{filename}"

    report = [
        "# 模块 B：研发效能与工作节律（提交历史）",
        "",
        f"生成日期：{now_str}",
        "",
        "## 1. 分析范围",
        "- 仓库：`apache/rocketmq`",
        "- 数据源：GitHub REST API（Commits API）",
        "- 清洗规则：过滤 Merge 提交；将提交时间统一换算为北京时间（UTC+8）",
        "- 工作日判定：使用 `chinesecalendar` 判断法定工作日/节假日（中国日历口径）",
        "",
        "## 2. 关键结论",
        f"- 样本期内共统计 {total_commits} 次提交，贡献者（按 name 去重）约 {unique_authors} 人。",
        f"- 节假日/周末提交占比为 {holiday_pct:.1f}%（{holiday_commits}/{total_commits}），可反映非工作日活跃度。",
        f"- 加班提交（节假日/周末 + 工作日非核心时段）占比为 {overtime_pct:.1f}%（{overtime_commits}/{total_commits}）。",
        f"- 仅看工作日样本，非核心时段提交占比为 {workday_overtime_pct:.1f}%（{workday_overtime_commits}/{workday_total}）。",
        "",
        "### 2.1 关键指标汇总",
        metrics,
        "",
        "### 2.2 贡献者提交量（Top 10）",
        top_authors_md,
        "",
        "## 3. 图表与解读",
        f"![节假日与周末提交占比]({fig('overtime_holiday_pie.png')})",
        f"- 展示节假日/周末提交与工作日提交的比例；当前样本节假日/周末提交占比为 {holiday_pct:.1f}%。",
        "",
        f"![工作日加班占比]({fig('overtime_workday_pie.png')})",
        f"- 在工作日样本内区分核心工时与非核心时段提交；非核心时段占比为 {workday_overtime_pct:.1f}%。",
        "",
        f"![工作日小时分布]({fig('overtime_workday_bar.png')})",
        "- 展示工作日每小时提交量分布；可用于观察是否存在早勤/晚间提交集中现象。",
        "",
        f"![周×小时提交热力图]({fig('commit_heatmap.png')})",
        "- 观察一周内不同小时的提交密度；可辅助识别典型协作节律与高峰时段。",
        "",
        f"![每日提交趋势]({fig('daily_commit_trend.png')})",
        "- 展示每日提交趋势并区分工作日/节假日；可用于观察版本迭代的周期性与波动。",
        "",
        "## 4. 局限性",
        "- GitHub API 可能受到限速或网络波动影响；本报告以采集到的样本为准。",
        "- `author name` 可能存在同名/改名/缺失，贡献者去重仅作为近似估计。",
        "- 节假日/工作日判定采用中国日历口径，不能代表全球分布式团队的真实工作日。",
    ]

    return "\n".join(report) + "\n"


def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    clean_csv_path = os.path.join(repo_root, "data", "module_b", "clean_commits.csv")
    report_path = os.path.join(repo_root, "data", "module_b", "REPORT.md")

    figures_rel_dir = "../../figures/module_b"

    df = load_and_enrich_clean_commits(clean_csv_path)
    md = generate_report(df, figures_rel_dir=figures_rel_dir)

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"[OK] 模块 B 子报告已生成: {report_path}")


if __name__ == "__main__":
    main()
