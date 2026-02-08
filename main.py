import sys
from pathlib import Path

def run():
    """
    项目统一入口脚本。
    实际上是 Module D (scripts/module_d/main.py) 的快捷方式。
    """
    # 获取项目根目录
    project_root = Path(__file__).resolve().parent
    
    # 将 scripts/module_d 加入 Python 搜索路径 (sys.path)
    # 这样 module_d 内部的 import (如 import runner) 才能找到同级文件
    module_d_path = project_root / "scripts" / "module_d"
    sys.path.insert(0, str(module_d_path))

    try:
        # 直接导入 Module D 的 main 函数
        # 注意：这里已经是 "from main" 了，因为我们把 module_d 加到了 path[0]
        from main import main as module_d_main
        
        # 执行
        module_d_main()
        
    except ImportError as e:
        print(f"[Error] 无法加载 Module D: {e}")
        print(f"请检查目录结构是否完整: {module_d_path}")
        sys.exit(1)
    except Exception as e:
        print(f"[Error] 运行过程中发生未捕获异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()
