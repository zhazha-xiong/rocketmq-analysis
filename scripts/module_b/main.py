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

def run_pipeline():
    print("="*60)
    print("Module B 分析流水线启动")
    print("="*60)

    # 1. 获取数据
    print("\n[Step 1/4] 获取最新提交数据 (get_git_data)")
    try:
        get_git_data.main()
    except Exception as e:
        print(f"数据获取中断: {e}")
        return False

    # 2. 清洗数据
    print("\n[Step 2/4] 清洗数据 (clean_git_data)")
    try:
        clean_git_data.main()
    except Exception as e:
        print(f"数据清洗失败: {e}")
        return False

    # 3. 可视化
    print("\n[Step 3/4] 生成图表 (visualizer)")
    try:
        visualizer.main()
    except Exception as e:
        print(f"可视化失败: {e}")
        return False

    # 4. 子报告
    print("\n[Step 4/4] 生成子报告 (report_generator)")
    try:
        report_generator.main()
    except Exception as e:
        print(f"子报告生成失败: {e}")
        return False

    print("\n" + "="*60)
    print("Module B 流水线执行成功！")
    print("="*60)
    return True

if __name__ == "__main__":
    success = run_pipeline()
    if not success:
        sys.exit(1)
