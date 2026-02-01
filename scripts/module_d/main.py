import os
import sys
import subprocess

def run_module(module_name, script_path, work_dir):
    print(f"\n{'#'*20} 开始运行 {module_name} {'#'*20}")
    print(f"脚本路径: {script_path}")
    print(f"工作目录: {work_dir}")
    
    try:
        # 使用当前 python 解释器执行子脚本
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=work_dir,  # 设置工作目录为项目根目录
            check=True
        )
        print(f"{'#'*20} {module_name} 运行完成 {'#'*20}\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[Error] {module_name} 执行失败，退出代码: {e.returncode}")
        return False
    except Exception as e:
        print(f"[Error] {module_name} 执行异常: {e}")
        return False

def main():
    # 获取当前脚本所在目录 (scripts/module_d)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取 scripts 目录
    scripts_dir = os.path.dirname(current_dir)
    # 获取项目根目录 (rocketmq-analysis)
    project_root = os.path.dirname(scripts_dir)
    
    print(f"项目根目录: {project_root}")
    
    # 定义各模块入口脚本路径 (相对于 scripts 目录)
    modules = [
        ("Module A (静态分析)", os.path.join(scripts_dir, "module_a", "main.py")),
        ("Module B (Git数据分析)", os.path.join(scripts_dir, "module_b", "main.py")),
        ("Module C (社区评估)", os.path.join(scripts_dir, "module_c", "main.py"))
    ]
    
    # 依次执行模块
    for name, script in modules:
        if not os.path.exists(script):
            print(f"[Error] 找不到脚本: {script}")
            sys.exit(1)
            
        success = run_module(name, script, project_root)
        if not success:
            print(f"[Fatal] {name} 失败，终止后续流程。")
            sys.exit(1)
            
    print("\n" + "="*60)
    print("所有模块 (A, B, C) 执行完毕！")
    print("="*60)

if __name__ == "__main__":
    main()
