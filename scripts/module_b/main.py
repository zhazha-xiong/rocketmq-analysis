import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    import get_git_data
    import clean_git_data
    import visualizer
    import report_generator
    from module_utils import repo_root_from, run_four_step_pipeline
except ImportError as e:
    print(f"[Error] 模块导入失败: {e}")
    sys.exit(1)

def run_pipeline():
    repo_root = repo_root_from(__file__)
    os.makedirs(os.path.join(repo_root, "data", "module_b"), exist_ok=True)
    os.makedirs(os.path.join(repo_root, "figures", "module_b"), exist_ok=True)
    commits_path = os.path.join(repo_root, "data", "module_b", "commits.csv")

    return run_four_step_pipeline(
        module_label="Module B",
        data_path_to_skip_fetch=commits_path,
        fetch_func=get_git_data.main,
        clean_func=clean_git_data.main,
        visualize_func=visualizer.main,
        report_func=report_generator.main,
    )

if __name__ == "__main__":
    success = run_pipeline()
    if not success:
        sys.exit(1)
