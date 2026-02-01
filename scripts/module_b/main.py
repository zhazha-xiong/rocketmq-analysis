import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    import get_git_data
    import clean_git_data
    import visualizer
    import report_generator
except ImportError as e:
    print(f"[Error] 模块导入失败: {e}")
    sys.exit(1)


def _repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _run_step(step_no: int, total_steps: int, title: str, func) -> bool:
    print(f"\n[Step {step_no}/{total_steps}] {title}")
    try:
        func()
        return True
    except Exception as e:
        print(f"[Error] {title} 失败: {e}")
        return False

def run_pipeline():
    total_steps = 4

    print("=" * 60)
    print("Module B 分析流水线启动")
    print("=" * 60)

    repo_root = _repo_root()
    commits_path = os.path.join(repo_root, "data", "module_b", "commits.csv")

    # 1) 数据爬取
    if os.path.exists(commits_path) and os.path.getsize(commits_path) > 0:
        print("\n[Info] 检测到本地提交数据，跳过数据拉取")
    else:
        if not _run_step(1, total_steps, "数据爬取 (get_git_data)", get_git_data.main):
            return False

    # 2) 数据清洗
    if not _run_step(2, total_steps, "数据清洗 (clean_git_data)", clean_git_data.main):
        return False

    # 3) 可视化
    if not _run_step(3, total_steps, "可视化 (visualizer)", visualizer.main):
        return False

    # 4) 报告生成
    if not _run_step(4, total_steps, "报告生成 (report_generator)", report_generator.main):
        return False

    print("\n" + "=" * 60)
    print("Module B 流水线执行成功！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_pipeline()
    if not success:
        sys.exit(1)
