import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Import config_utils
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
    # Fallback or error
    print(f"Warning: Module D loading config failed: {e}")
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    FIGURES_DIR = PROJECT_ROOT / "figures"
    OUTPUT_DIR = PROJECT_ROOT / "docs"

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger("ModuleD")

def get_env(key, default=None):
    load_dotenv(PROJECT_ROOT / "scripts" / ".env")
    return os.getenv(key, default)