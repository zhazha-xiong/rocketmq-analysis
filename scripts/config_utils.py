import yaml
import os
import sys
from pathlib import Path

# 定义项目根目录（基于此脚本位于 scripts/ 目录的假设）
# scripts/config_utils.py -> scripts/ -> root/
ROOT_DIR = Path(__file__).parent.parent

def load_config(config_file="config.yaml"):
    """
    加载项目根目录下的配置文件。
    
    Args:
        config_file (str): 配置文件名，默认为 "config.yaml"
    
    Returns:
        dict: 配置字典
    
    Raises:
        FileNotFoundError: 如果找不到配置文件
    """
    # 优先查找 ROOT_DIR
    config_path = ROOT_DIR / config_file
    
    if not config_path.exists():
        # 尝试从当前工作目录查找
        config_path = Path(os.getcwd()) / config_file

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file '{config_file}' not found.\n"
            f"Searched paths:\n"
            f"  - {ROOT_DIR / config_file}\n"
            f"  - {Path(os.getcwd()) / config_file}\n"
            "Please ensure config.yaml exists in the project root."
        )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if not config:
                return {}
            
            # 注入路径助手，方便其他模块使用绝对路径
            if 'paths' not in config:
                config['paths'] = {}
            
            config['paths']['root'] = str(ROOT_DIR)
            
            # 处理 output 目录的绝对路径
            output_cfg = config.get('output', {})
            config['paths']['data'] = str(ROOT_DIR / output_cfg.get('data_dir', 'data'))
            config['paths']['figures'] = str(ROOT_DIR / output_cfg.get('figures_dir', 'figures'))
            config['paths']['docs'] = str(ROOT_DIR / output_cfg.get('docs_dir', 'docs'))
            
            return config
            
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        raise

if __name__ == "__main__":
    # 测试代码
    try:
        cfg = load_config()
        print(f"Successfully loaded config from project: {cfg.get('project', {}).get('name')}")
        print(f"Data directory: {cfg['paths']['data']}")
    except Exception as e:
        print(f"Failed to load config: {e}")
