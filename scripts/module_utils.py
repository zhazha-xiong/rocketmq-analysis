import json
import os
from typing import Any, Callable

import requests
from dotenv import load_dotenv


def repo_root_from(current_file: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(current_file), "..", ".."))


def file_ready(path: str) -> bool:
    return os.path.exists(path) and os.path.getsize(path) > 0


def run_step(step_no: int, total_steps: int, title: str, func: Callable[[], Any]) -> bool:
    print(f"\n[Step {step_no}/{total_steps}] {title}")
    try:
        func()
        return True
    except Exception as e:
        print(f"[Error] {title} 失败: {e}")
        return False


def run_four_step_pipeline(
    *,
    module_label: str,
    data_path_to_skip_fetch: str,
    fetch_func: Callable[[], Any],
    clean_func: Callable[[], Any],
    visualize_func: Callable[[], Any],
    report_func: Callable[[], Any],
) -> bool:
    total_steps = 4

    print("=" * 60)
    print(f"{module_label} 分析流水线启动")
    print("=" * 60)

    if file_ready(data_path_to_skip_fetch):
        print("\n[Info] 检测到本地数据，跳过数据拉取")
    else:
        if not run_step(1, total_steps, "数据爬取 (get_git_data)", fetch_func):
            return False

    if not run_step(2, total_steps, "数据清洗 (clean_git_data)", clean_func):
        return False

    if not run_step(3, total_steps, "可视化 (visualizer)", visualize_func):
        return False

    if not run_step(4, total_steps, "报告生成 (report_generator)", report_func):
        return False

    print("\n" + "=" * 60)
    print(f"{module_label} 流水线执行成功！")
    print("=" * 60)
    return True


def load_github_token(*, missing_hint: str, caller_file: str | None = None) -> str:
    # 统一支持“公共 .env”：优先模块目录，其次 scripts/.env，再次仓库根目录 .env，最后 cwd/.env
    candidates: list[str] = []

    if caller_file:
        candidates.append(os.path.join(os.path.dirname(os.path.abspath(caller_file)), ".env"))

    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(scripts_dir, ".env"))

    repo_root = os.path.abspath(os.path.join(scripts_dir, ".."))
    candidates.append(os.path.join(repo_root, ".env"))

    candidates.append(os.path.join(os.getcwd(), ".env"))

    seen: set[str] = set()
    for env_path in candidates:
        if env_path in seen:
            continue
        seen.add(env_path)

        if os.path.exists(env_path):
            load_dotenv(dotenv_path=env_path)
            break

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError(missing_hint)

    return token


def github_headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def github_get_json(
    url: str,
    headers: dict[str, str],
    params: dict[str, Any] | None = None,
    timeout: int = 30,
) -> Any:
    """简单的 GitHub API GET 请求封装"""
    resp = requests.get(url, headers=headers, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def write_json(data: Any, path: str, indent: int = 2) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def ensure_local_repo(owner: str, name: str, target_dir: str) -> None:
    """
    确保指定仓库已克隆到本地 target_dir。
    如果 target_dir 为空或不存在，则执行 git clone。
    如果已存在且非空，则跳过（假设已存在）。
    """
    import subprocess
    from pathlib import Path

    target_path = Path(target_dir)
    
    # 简单的非空检查：如果存在且包含 .git 目录，认为已克隆
    if target_path.exists() and (target_path / ".git").exists():
        print(f"[Info] 仓库已存在于 {target_dir}，跳过克隆。")
        return

    # 构造 Clone URL (优先尝试 HTTPS)
    # 对于公开仓库，HTTPS 不需要 Token，比较通用
    repo_url = f"https://github.com/{owner}/{name}.git"
    
    print(f"[Info] 正在克隆 {repo_url} 到 {target_dir} ...")
    
    try:
        subprocess.run(
            ["git", "clone", repo_url, str(target_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"[Success] 克隆完成: {target_dir}")
    except subprocess.CalledProcessError as e:
        print(f"[Error] Git Clone 失败: {e.stderr}")
        raise RuntimeError(f"无法自动克隆仓库 {owner}/{name}") from e
