import yaml
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

def load_config(config_file="config.yaml"):
    """加载配置并注入绝对路径。"""
    config_path = ROOT_DIR / config_file
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found at: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}
        
    # 注入绝对路径
    config.setdefault('paths', {})['root'] = str(ROOT_DIR)
    
    output = config.get('output', {})
    for key, val in [('data', 'data_dir'), ('figures', 'figures_dir'), ('docs', 'docs_dir')]:
        config['paths'][key] = str(ROOT_DIR / output.get(val, key))
        
    return config

if __name__ == "__main__":
    print(load_config().get('project', {}).get('name'))
