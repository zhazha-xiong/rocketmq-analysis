"""
使用Lizard进行代码复杂度分析
"""
import subprocess
import pandas as pd
import os
import re
import sys
def run_lizard_scan(repo_paths, output_file):
    """
    对指定仓库运行Lizard扫描
    
    Args:
        repo_paths: 仓库路径列表
        output_file: 输出CSV文件路径
    """
    all_results = []
    
    for repo_path in repo_paths:
        # 获取仓库名称：如果是子目录，保留父目录/子目录格式
        if 'rocketmq-clients' in repo_path and repo_path.endswith('python'):
            repo_name = "rocketmq-clients/python"
        else:
            repo_name = os.path.basename(repo_path)
        print(f"\n正在分析: {repo_name}")
        print("=" * 50)
        
        # 构建Lizard命令
        # -l python: 只分析Python文件
        # --csv: 输出CSV格式
        cmd = [
            sys.executable,
            '-m', 'lizard',
            '-l', 'python',
            '--csv',
            repo_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                # 解析CSV输出
                lines = result.stdout.strip().split('\n')
                
                # 跳过前两行（标题和分隔符）
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 4:
                            all_results.append({
                                'repository': repo_name,
                                'nloc': int(parts[0]) if parts[0].isdigit() else 0,
                                'ccn': int(parts[1]) if parts[1].isdigit() else 0,
                                'token': int(parts[2]) if parts[2].isdigit() else 0,
                                'param': int(parts[3]) if parts[3].isdigit() else 0,
                                'function': parts[5] if len(parts) > 5 else '',
                                'file': parts[7] if len(parts) > 7 else ''
                            })
                
                print(f"分析了 {len([r for r in all_results if r['repository'] == repo_name])} 个函数")
            
        except Exception as e:
            print(f"分析失败: {e}")
            continue
    
    # 创建DataFrame并保存
    df = pd.DataFrame(all_results)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n结果已保存到: {output_file}")
    
    return df

def analyze_complexity(df):
    """
    分析代码复杂度并标记问题函数
    
    根据方案中的阈值:
    - 高圈复杂度: CCN > 15
    - 过长函数: NLOC > 80
    - 过多参数: param > 5
    """
    print("\n" + "=" * 50)
    print("代码复杂度分析")
    print("=" * 50)
    
    # 标记问题
    df['high_complexity'] = df['ccn'] > 15
    df['too_long'] = df['nloc'] > 80
    df['too_many_params'] = df['param'] > 5
    
    # 统计
    total_functions = len(df)
    high_ccn_count = df['high_complexity'].sum()
    long_func_count = df['too_long'].sum()
    many_params_count = df['too_many_params'].sum()
    
    print(f"\n总函数数: {total_functions}")
    print(f"高复杂度函数 (CCN > 15): {high_ccn_count} ({high_ccn_count/total_functions*100:.1f}%)")
    print(f"过长函数 (NLOC > 80): {long_func_count} ({long_func_count/total_functions*100:.1f}%)")
    print(f"参数过多函数 (param > 5): {many_params_count} ({many_params_count/total_functions*100:.1f}%)")
    
    # 显示Top 10最复杂的函数
    print("\nTop 10 最高复杂度函数:")
    top_complex = df.nlargest(10, 'ccn')[['repository', 'function', 'ccn', 'nloc', 'param', 'file']]
    print(top_complex.to_string(index=False))
    
    return df

if __name__ == "__main__":
    # 定义要扫描的仓库路径
    repos = [
        "temp_repos/rocketmq-client-python",
        "temp_repos/rocketmq-clients/python"
    ]
    
    # 运行分析
    df_lizard = run_lizard_scan(repos, "data/module_a/lizard_raw.csv")
    
    # 复杂度分析并标记问题
    df_analyzed = analyze_complexity(df_lizard)
    
    # 保存分析结果
    df_analyzed.to_csv("data/module_a/lizard_results.csv", index=False, encoding='utf-8-sig')
    print("\n分析结果已保存到: data/module_a/lizard_results.csv")