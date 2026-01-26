import os
import json
import re
from datetime import datetime


def main() -> None:
    # 1. 基础路径配置
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    data_dir = os.path.join(repo_root, "data", "module_c")

    # 2. 加载原始数据
    commits_path = os.path.join(data_dir, "commits.json")
    prs_path = os.path.join(data_dir, "pull_requests.json")
    runs_path = os.path.join(data_dir, "workflow_runs.json")
    releases_path = os.path.join(data_dir, "releases.json")
    files_path = os.path.join(data_dir, "files_structure.json")

    # 检查数据完整性
    if not os.path.exists(commits_path):
        raise RuntimeError(f"数据文件缺失: {commits_path}，请先运行 get_git_data.py")

    with open(commits_path, "r", encoding="utf-8") as f: commits = json.load(f)
    with open(prs_path, "r", encoding="utf-8") as f: prs = json.load(f)
    with open(runs_path, "r", encoding="utf-8") as f: runs = json.load(f)
    with open(releases_path, "r", encoding="utf-8") as f: releases = json.load(f)
    with open(files_path, "r", encoding="utf-8") as f: files_status = json.load(f)

    print("===开始数据清洗与评分计算===")

    # 3. 指标计算逻辑
    
    # --- 维度 1: 版本控制 (25分) ---
    # 1.1 Commit 规范性检查 (15分)
    valid_commits = 0
    pattern = re.compile(r"^(feat|fix|docs|style|refactor|test|chore|perf|build|ci|revert)(\(.+\))?:", re.IGNORECASE)
    for c in commits:
        msg = c.get("commit", {}).get("message", "").splitlines()[0]
        if pattern.match(msg):
            valid_commits += 1
    score_vc_commit = (valid_commits / len(commits)) * 15 if commits else 0

    # 1.2 PR 流程规范性检查 (10分)
    valid_prs = 0
    for pr in prs:
        if pr.get("assignee") or pr.get("requested_reviewers") or pr.get("labels"):
            valid_prs += 1
    score_vc_pr = (valid_prs / len(prs)) * 10 if prs else 0
    
    score_version_control = score_vc_commit + score_vc_pr

    # --- 维度 2: 持续集成 (20分) ---
    # 2.1 Workflow 运行成功率 (15分)
    success_runs = sum(1 for r in runs if r.get("conclusion") == "success")
    score_ci_health = (success_runs / len(runs)) * 15 if runs else 0
    
    # 2.2 CI 配置检查 (5分)
    score_ci_config = 5 if files_status.get(".github/workflows") else 0
    
    score_ci = score_ci_health + score_ci_config

    # --- 维度 3: 社区治理 (30分) ---
    # 3.1 关键文档检查 (15分)
    docs = ["LICENSE", "README.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md"]
    found_docs = sum(1 for d in docs if files_status.get(d))
    score_gov_docs = found_docs * 3.75

    # 3.2 版本发布周期 (15分)
    score_gov_release = 0
    if len(releases) >= 2:
        dates = [datetime.strptime(r["published_at"], "%Y-%m-%dT%H:%M:%SZ") for r in releases[:10] if r.get("published_at")]
        if len(dates) >= 2:
            deltas = [(dates[i] - dates[i+1]).days for i in range(len(dates)-1)]
            avg_days = sum(deltas) / len(deltas)
            score_gov_release = 15 if avg_days <= 90 else max(0, 15 - (avg_days - 90) * 0.1)
    elif len(releases) == 1:
        score_gov_release = 10
    
    score_governance = score_gov_docs + score_gov_release

    # --- 维度 4: 代码质量 (25分) ---
    # 4.1 测试配置检查 (10分)
    score_cq_test = 10 if files_status.get("pom.xml") else 0 
    # 4.2 代码规范配置检查 (15分)
    score_cq_style = 15 if files_status.get(".editorconfig") else 0
    
    score_quality = score_cq_test + score_cq_style

    # 4. 结果汇总与持久化
    final_data = {
        "version_control": {
            "total": round(score_version_control, 2),
            "commit_norm": round(score_vc_commit, 2),
            "pr_process": round(score_vc_pr, 2)
        },
        "ci_health": {
            "total": round(score_ci, 2),
            "run_rate": round(score_ci_health, 2), 
            "config_exist": score_ci_config
        },
        "governance": {
            "total": round(score_governance, 2),
            "docs": score_gov_docs, 
            "release_cycle": round(score_gov_release, 2)
        },
        "code_quality": {
            "total": round(score_quality, 2),
            "test_config": score_cq_test,
            "style_config": score_cq_style
        },
        "total_score": round(score_version_control + score_ci + score_governance + score_quality, 2),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print(f"[INFO] 评分结果: {final_data['total_score']} / 100")
    
    print("-" * 40)
    print(f"1. 版本控制: {final_data['version_control']['total']:>5} / 25")
    print(f"   - Commit规范: {final_data['version_control']['commit_norm']:>5} / 15")
    print(f"   - PR流程:     {final_data['version_control']['pr_process']:>5} / 10")
    
    print(f"2. 持续集成: {final_data['ci_health']['total']:>5} / 20")
    print(f"   - 运行成功率: {final_data['ci_health']['run_rate']:>5} / 15")
    print(f"   - CI配置:     {final_data['ci_health']['config_exist']:>5} / 5")
    
    print(f"3. 社区治理: {final_data['governance']['total']:>5} / 30")
    print(f"   - 关键文档:   {final_data['governance']['docs']:>5} / 15")
    print(f"   - 发布周期:   {final_data['governance']['release_cycle']:>5} / 15")
    
    print(f"4. 代码质量: {final_data['code_quality']['total']:>5} / 25")
    print(f"   - 测试配置:   {final_data['code_quality']['test_config']:>5} / 10")
    print(f"   - 代码规范:   {final_data['code_quality']['style_config']:>5} / 15")
    print("-" * 40)

    out_path = os.path.join(data_dir, "clean_scores.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"[OK] 已清洗数据并保存至: {out_path}")


if __name__ == "__main__":
    main()
