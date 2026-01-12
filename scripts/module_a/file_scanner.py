"""
扫描目标仓库中的所有Python文件
"""
import os
import pandas as pd
from pathlib import Path

def scan_python_files(repo_paths):
    """
    扫描指定仓库中的所有.py文件
    
    Args:
        repo_paths: 仓库路径列表
    
    Returns:
        DataFrame包含文件路径和所属仓库
    """
    files_data = []
    
    for repo_path in repo_paths:
        repo_name = os.path.basename(repo_path)
        print(f"扫描仓库: {repo_name}")
        
        for root, dirs, files in os.walk(repo_path):
            # 跳过虚拟环境、测试数据等目录
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', '.venv', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)
                    
                    files_data.append({
                        'repository': repo_name,
                        'absolute_path': file_path,
                        'relative_path': rel_path,
                        'file_size': os.path.getsize(file_path)
                    })
    
    df = pd.DataFrame(files_data)
    print(f"\n总计发现 {len(df)} 个Python文件")
    print(f"rocketmq-client-python: {len(df[df['repository'] == 'rocketmq-client-python'])} 个")
    print(f"rocketmq-clients: {len(df[df['repository'] == 'rocketmq-clients'])} 个")
    
    return df

if __name__ == "__main__":
    # 定义要扫描的仓库路径
    repos = [
        "temp_repos/rocketmq-client-python",
        "temp_repos/rocketmq-clients/python"  # 只扫描Python部分
    ]
    
    # 扫描文件
    df_files = scan_python_files(repos)
    
    # 保存结果
    output_path = "data/module_a/python_files.csv"
    df_files.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n文件清单已保存到: {output_path}")