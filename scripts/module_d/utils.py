import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# 初始化路径
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