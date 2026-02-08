import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# 导入 config_utils
sys.path.append(str(Path(__file__).parent.parent))
from config_utils import load_config

# 初始化路径
try:
    CONFIG = load_config()
    PROJECT_ROOT = Path(CONFIG['paths']['root'])
    DATA_DIR = Path(CONFIG['paths']['data'])
    FIGURES_DIR = Path(CONFIG['paths']['figures'])
    OUTPUT_DIR = Path(CONFIG['paths']['docs'])
except Exception as e:
    # 回退或报错
    print(f"Warning: Module D loading config failed: {e}")
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    FIGURES_DIR = PROJECT_ROOT / "figures"
    OUTPUT_DIR = PROJECT_ROOT / "docs"

def setup_logging():
    """配置并返回日志记录器"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger("ModuleD")

def get_env(key, default=None):
    """从 .env 文件加载环境变量"""
    load_dotenv(PROJECT_ROOT / "scripts" / ".env")
    return os.getenv(key, default)