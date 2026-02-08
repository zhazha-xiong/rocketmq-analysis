import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config_utils import load_config
    
    import get_git_data
    import clean_git_data
    import visualizer
    import report_generator
    from module_utils import repo_root_from, run_four_step_pipeline
except ImportError as e:
    print(f"[Error] 模块导入失败: {e}")
    sys.exit(1)

CONFIG = load_config()

def run_pipeline():
    data_dir = Path(CONFIG['paths']['data']) / "module_b"
    figs_dir = Path(CONFIG['paths']['figures']) / "module_b"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(figs_dir, exist_ok=True)
    
    commits_path = data_dir / "commits.csv"

    return run_four_step_pipeline(
        module_label="Module B",
        data_path_to_skip_fetch=str(commits_path),
        fetch_func=get_git_data.main,
        clean_func=clean_git_data.main,
        visualize_func=visualizer.main,
        report_func=report_generator.main,
    )

if __name__ == "__main__":
    success = run_pipeline()
    if not success:
        sys.exit(1)
