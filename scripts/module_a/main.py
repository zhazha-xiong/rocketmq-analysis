import os
import sys
import argparse
import file_scanner
import bandit_scanner
import lizard_scanner
import visualizer
import report_generator

def ensure_directories():
    """确保所需目录存在"""
    dirs = [
        "data/module_a",
        "figures/module_a",
        "temp_repos"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"目录已就绪: {d}")

def check_repos():
    """检查目标仓库是否已克隆"""
    repos = [
        "temp_repos/rocketmq-client-python",
        "temp_repos/rocketmq-clients"
    ]
    
    missing = [r for r in repos if not os.path.exists(r)]
    
    if missing:
        print("\n以下仓库尚未克隆:")
        for repo in missing:
            print(f"  - {repo}")
        print("\n请先执行以下命令克隆仓库:")
        print("  cd temp_repos")
        print("  git clone https://github.com/apache/rocketmq-client-python.git")
        print("  git clone https://github.com/apache/rocketmq-clients.git")
        return False
    
    return True

def run_all():
    """运行完整分析流程"""
    print("=" * 60)
    print("模块A：Python静态分析 - 完整流程")
    print("=" * 60)
    
    # Step 1: 准备工作
    print("\n[步骤 1/5] 准备工作...")
    ensure_directories()
    
    if not check_repos():
        sys.exit(1)
    
    # Step 2: 文件扫描
    print("\n[步骤 2/5] 扫描Python文件...")
    repos = [
        "temp_repos/rocketmq-client-python",
        "temp_repos/rocketmq-clients/python"
    ]
    df_files = file_scanner.scan_python_files(repos)
    df_files.to_csv("data/module_a/python_files.csv", index=False, encoding='utf-8-sig')
    
    # Step 3: Bandit安全扫描
    print("\n[步骤 3/5] 运行Bandit安全扫描...")
    raw_bandit = bandit_scanner.run_bandit_scan(repos, "data/module_a/bandit_raw.json")
    df_bandit = bandit_scanner.parse_bandit_results(raw_bandit)
    df_bandit.to_csv("data/module_a/bandit_results.csv", index=False, encoding='utf-8-sig')
    bandit_scanner.analyze_bandit_results(df_bandit)
    
    # Step 4: Lizard复杂度分析
    print("\n[步骤 4/5] 运行Lizard复杂度分析...")
    df_lizard = lizard_scanner.run_lizard_scan(repos, "data/module_a/lizard_raw.csv")
    df_analyzed = lizard_scanner.analyze_complexity(df_lizard)
    df_analyzed.to_csv("data/module_a/lizard_results.csv", index=False, encoding='utf-8-sig')
    
    # Step 5: 生成可视化图表
    print("\n[步骤 5/6] 生成可视化图表...")
    output_dir = "figures/module_a"
    visualizer.plot_bandit_severity(df_bandit, output_dir)
    visualizer.plot_bandit_issues(df_bandit, output_dir)
    visualizer.plot_complexity_distribution(df_analyzed, output_dir)
    visualizer.plot_top_complex_functions(df_analyzed, output_dir)
    visualizer.plot_repository_comparison(df_bandit, df_analyzed, output_dir)
    
    # Step 6: 生成子报告
    print("\n[步骤 6/6] 生成子报告（REPORT.md）...")
    report_generator.main()
    
    # 完成
    print("\n" + "=" * 60)
    print("模块A分析完成！")
    print("=" * 60)
    print("\n生成的文件:")
    print("  数据文件:")
    print("    - data/module_a/python_files.csv")
    print("    - data/module_a/bandit_results.csv")
    print("    - data/module_a/lizard_results.csv")
    print("  图表文件:")
    print("    - figures/module_a/*.png")
    print("  子报告:")
    print("    - data/module_a/REPORT.md")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='模块A：Python静态分析')
    parser.add_argument('--step', type=str, choices=['scan', 'bandit', 'lizard', 'viz', 'all'],
                        default='all', help='运行特定步骤或完整流程')
    
    args = parser.parse_args()
    
    if args.step == 'all':
        run_all()
    elif args.step == 'scan':
        print("运行文件扫描...")