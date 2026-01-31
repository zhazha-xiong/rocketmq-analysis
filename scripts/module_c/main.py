import os
import sys
import subprocess

def run_step(step_name, script_name):
    print(f"\n{'='*20} {step_name} {'='*20}")
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    try:
        if not os.path.exists(script_path):
            print(f"[Error] 脚本未找到: {script_path}")
            return False
            
        result = subprocess.run([sys.executable, script_path], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"[Error] {step_name} 失败: {e}")
        return False
    except Exception as e:
        print(f"[Error] 执行异常: {e}")
        return False

def main():
    print("启动模块 C 自动化评估流程...")
    
    # 1. 获取数据
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "module_c")
    commits_file = os.path.join(data_dir, "commits.json")
    
    if not os.path.exists(commits_file):
        print("[Info] 本地数据缺失，开始拉取数据...")
        if not run_step("1. 获取 GitHub 数据", "get_git_data.py"): return
    else:
        print("[Info] 检测到本地数据，跳过数据拉取")

    # 2. 清洗与评分
    if not run_step("2. 数据清洗与评分", "clean_git_data.py"): return

    # 3. 可视化
    if not run_step("3. 生成可视化图表", "visualizer.py"): return
    
    # 4. 生成报告
    if not run_step("4. 生成 Markdown 报告", "report_generator.py"): return

    print(f"\n{'='*20} 流程结束 {'='*20}")
    print(f"评估报告已生成: {os.path.join(data_dir, 'REPORT.md')}")
    print(f"图表已保存至: figures/module_c/")

if __name__ == "__main__":
    main()