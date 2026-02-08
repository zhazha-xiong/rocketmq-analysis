import os
import sys
import argparse
from pathlib import Path

# Add scripts directory to path to import config_utils
sys.path.append(str(Path(__file__).parent.parent))
from config_utils import load_config

import file_scanner
import bandit_scanner
import lizard_scanner
import visualizer
import report_generator

# Load configuration
CONFIG = load_config()

def ensure_directories():
    """确保所需目录存在"""
    # Use paths from config
    data_dir =  Path(CONFIG['paths']['data']) / "module_a"
    figs_dir = Path(CONFIG['paths']['figures']) / "module_a"
    
    # 尝试自动创建配置的扫描路径（方便用户直接 clone）
    scan_paths = get_raw_scan_paths()
    root = Path(CONFIG['paths']['root'])
    
    dirs = [data_dir, figs_dir]
    
    for p in scan_paths:
        full_path = root / p
        # 只有当路径看起来像是在项目内的目录时才尝试创建（避免创建奇怪的绝对路径）
        if not full_path.exists() and not full_path.is_absolute():
             dirs.append(full_path)
        elif not full_path.exists() and full_path.is_relative_to(root):
             dirs.append(full_path)

    for d in dirs:
        try:
            os.makedirs(d, exist_ok=True)
            print(f"目录已就绪: {d}")
        except Exception as e:
            print(f"[Warn] 无法创建目录 {d}: {e}")

def get_raw_scan_paths():
    raw_paths = CONFIG.get('module_a', {}).get('scan_paths', 'temp_repos')
    if isinstance(raw_paths, str):
        return [raw_paths]
    return list(raw_paths)

def get_scan_targets():
    """获取待扫描的目标路径"""
    # From config: module_a.scan_paths
    root = Path(CONFIG['paths']['root'])
    scan_paths = get_raw_scan_paths()
    
    targets = []
    for p in scan_paths:
        target = root / p
        if target.exists():
            targets.append(target)
        else:
            print(f"[Warn] 扫描路径不存在: {target}")
    
    return targets

def run_all():
    """运行完整分析流程"""
    print("=" * 60)
    print("模块A：Python静态分析 - 完整流程")
    print("=" * 60)
    
    if not CONFIG.get('module_a', {}).get('enabled', True):
        print("Module A is disabled in config.")
        return

    # Step 1: 准备工作
    print("\n[步骤 1/5] 准备工作...")
    ensure_directories()
    targets = get_scan_targets()
    if not targets:
        print("未找到有效扫描路径，退出。")
        return
    
    # Step 2: 文件扫描
    print("\n[步骤 2/6] 扫描Python文件...")
    # 转换路径为字符串以兼容旧接口
    target_strs = [str(t) for t in targets]
    
    data_path = Path(CONFIG['paths']['data']) / "module_a"
    figs_path = Path(CONFIG['paths']['figures']) / "module_a"

    try:
        df_files = file_scanner.scan_python_files(target_strs)
        df_files.to_csv(data_path / "python_files.csv", index=False, encoding='utf-8-sig')
    except Exception as e:
        print(f"[Error] 文件扫描失败: {e}")
        return

    # Step 3: Bandit安全扫描
    print("\n[步骤 3/6] 运行Bandit安全扫描...")
    try:
        raw_bandit_path = data_path / "bandit_raw.json"
        raw_bandit = bandit_scanner.run_bandit_scan(target_strs, str(raw_bandit_path))
        df_bandit = bandit_scanner.parse_bandit_results(raw_bandit)
        df_bandit.to_csv(data_path / "bandit_results.csv", index=False, encoding='utf-8-sig')
        bandit_scanner.analyze_bandit_results(df_bandit)
    except Exception as e:
         print(f"[Error] Bandit扫描失败: {e}")
         df_bandit = None

    # Step 4: Lizard复杂度分析
    print("\n[步骤 4/6] 运行Lizard复杂度分析...")
    try:
        df_lizard = lizard_scanner.run_lizard_scan(target_strs, str(data_path / "lizard_raw.csv"))
        df_analyzed = lizard_scanner.analyze_complexity(df_lizard)
        df_analyzed.to_csv(data_path / "lizard_results.csv", index=False, encoding='utf-8-sig')
    except Exception as e:
        print(f"[Error] Lizard扫描失败: {e}")
        df_analyzed = None
    
    # Step 5: 生成可视化图表
    print("\n[步骤 5/6] 生成可视化图表...")
    try:
        if df_bandit is not None and df_analyzed is not None:
             visualizer.plot_bandit_severity(df_bandit, str(figs_path))
             visualizer.plot_bandit_issues(df_bandit, str(figs_path))
             visualizer.plot_complexity_distribution(df_analyzed, str(figs_path))
             visualizer.plot_top_complex_functions(df_analyzed, str(figs_path))
             # Visualizer might need update if it depends on specific 'Repository' column matching hardcoded names
             visualizer.plot_repository_comparison(df_bandit, df_analyzed, str(figs_path))
    except Exception as e:
        print(f"[Warn] 可视化生成部分失败: {e}")

    # Step 6: 生成子报告
    print("\n[步骤 6/6] 生成子报告（REPORT.md）...")
    # Report generator needs to be config aware too, but let's assume it finds files by relative path or we update it later.
    # For now, it seems report_generator.main() is self-contained.
    try:
        report_generator.main()
    except Exception as e:
        print(f"[Warn] 报告生成失败: {e}")
    
    # 完成
    print("\n" + "=" * 60)
    print("模块A分析完成！")
    print("=" * 60)
    print("\n生成的文件:")
    print(f"  数据文件 (在 {data_path}):")
    print("    - python_files.csv")
    print("    - bandit_results.csv")
    print("    - lizard_results.csv")
    print(f"  图表文件 (在 {figs_path}):")
    print("    - *.png")
    print("  子报告:")
    print("    - REPORT.md")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='模块A：Python静态分析')
    parser.add_argument('--step', type=str, choices=['scan', 'bandit', 'lizard', 'viz', 'all'],
                        default='all', help='运行特定步骤或完整流程')
    
    args = parser.parse_args()
    
    if args.step == 'all':
        run_all()
    elif args.step == 'scan':
        print("运行文件扫描...")