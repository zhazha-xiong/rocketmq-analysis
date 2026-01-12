"""
使用Bandit进行Python代码安全漏洞扫描
"""
import subprocess
import json
import pandas as pd
import os

def run_bandit_scan(repo_paths, output_file):
    """
    对指定仓库运行Bandit扫描
    
    Args:
        repo_paths: 仓库路径列表
        output_file: 输出JSON文件路径
    """
    all_results = []
    
    for repo_path in repo_paths:
        repo_name = os.path.basename(repo_path)
        print(f"\n正在扫描: {repo_name}")
        print("=" * 50)
        
        # 构建Bandit命令
        # -r: 递归扫描
        # -f json: 输出JSON格式
        cmd = [
            'bandit',
            '-r', repo_path,
            '-f', 'json',
            '--exclude', '**/test_*.py,**/tests/**'  # 排除测试文件
        ]
        
        try: 
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout and result.stdout.strip():
                try:
                    # 清理stdout：Bandit可能会在JSON前输出进度条
                    stdout_clean = result.stdout
                    # 找到第一个 '{' 的位置，从那里开始解析JSON
                    json_start = stdout_clean.find('{')
                    if json_start > 0:
                        stdout_clean = stdout_clean[json_start:]
                    
                    data = json.loads(stdout_clean)
                    
                    # 为每个结果添加仓库信息
                    for issue in data.get('results', []):
                        issue['repository'] = repo_name
                        all_results.append(issue)
                    
                    print(f"发现 {len(data.get('results', []))} 个问题")
                    
                    # 显示问题级别统计
                    if data.get('results'):
                        severity_counts = {}
                        for issue in data.get('results', []):
                            sev = issue.get('issue_severity', 'UNKNOWN')
                            severity_counts[sev] = severity_counts.get(sev, 0) + 1
                        print(f"  级别分布: {severity_counts}")
                        
                except json.JSONDecodeError as je:
                    print(f"JSON解析失败: {je}")
                    # 不打印stderr，因为那是正常的日志信息
                    print(f"发现 0 个问题")
            else:
                print(f"Bandit无输出，可能该目录没有Python文件")
                print(f"发现 0 个问题")
            
        except Exception as e:
            print(f"扫描失败: {e}")
            continue
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n原始结果已保存到: {output_file}")
    return all_results

def parse_bandit_results(results):
    """
    解析Bandit结果并生成DataFrame
    """
    parsed_data = []
    
    for issue in results:
        parsed_data.append({
            'repository': issue.get('repository', ''),
            'file': issue.get('filename', ''),
            'line_number': issue.get('line_number', 0),
            'issue_type': issue.get('test_id', ''),
            'issue_name': issue.get('test_name', ''),
            'severity': issue.get('issue_severity', ''),
            'confidence': issue.get('issue_confidence', ''),
            'code': issue.get('code', '').strip(),
            'description': issue.get('issue_text', '')
        })
    
    return pd.DataFrame(parsed_data)

def analyze_bandit_results(df):
    """
    统计分析Bandit扫描结果
    """
    print("\n" + "=" * 50)
    print("Bandit扫描结果统计")
    print("=" * 50)
    
    print(f"\n总问题数: {len(df)}")
    
    # 如果没有发现问题，直接返回
    if len(df) == 0:
        print("\n未发现安全问题")
        return
    
    print("\n按严重性分类:")
    print(df['severity'].value_counts())
    
    print("\n按置信度分类:")
    print(df['confidence'].value_counts())
    
    print("\n按问题类型分类 (Top 10):")
    print(df['issue_name'].value_counts().head(10))
    
    print("\n高危问题 (High Severity):")
    high_severity = df[df['severity'] == 'HIGH']
    print(f"数量: {len(high_severity)}")
    if len(high_severity) > 0:
        print("\n问题类型分布:")
        print(high_severity['issue_name'].value_counts())

if __name__ == "__main__":
    # 定义要扫描的仓库路径
    repos = [
        "temp_repos/rocketmq-client-python",
        "temp_repos/rocketmq-clients/python"
    ]
    
    # 运行扫描
    raw_results = run_bandit_scan(repos, "data/module_a/bandit_raw.json")
    
    # 解析结果
    df_bandit = parse_bandit_results(raw_results)
    
    # 保存解析后的结果
    df_bandit.to_csv("data/module_a/bandit_results.csv", index=False, encoding='utf-8-sig')
    print("\n解析结果已保存到: data/module_a/bandit_results.csv")
    
    # 统计分析
    analyze_bandit_results(df_bandit)