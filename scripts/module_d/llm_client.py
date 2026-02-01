import openai
import os
from utils import get_env, PROJECT_ROOT, setup_logging

logger = setup_logging()

def call_llm(content):
    # 1. 获取配置
    api_key = get_env("LLM_API_KEY")
    base_url = get_env("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model = get_env("LLM_MODEL_NAME", "qwen-max")

    if not api_key:
        logger.error("未找到 LLM_API_KEY，请检查 .env 文件")
        return "错误：未配置 API Key，无法生成 AI 洞察。"

    # 2. 初始化客户端 (设置超时时间)
    client = openai.OpenAI(
        api_key=api_key, 
        base_url=base_url,
        timeout=120.0  # 增加超时时间到 2 分钟
    )
    
    # 3. 读取提示词文件并增加安全检查
    prompt_dir = PROJECT_ROOT / "scripts" / "module_d" / "prompts"
    system_file = prompt_dir / "system.md"
    user_file = prompt_dir / "user_template.md"

    if not system_file.exists() or not user_file.exists():
        logger.error(f"提示词文件不存在: {prompt_dir}")
        return "错误：提示词模板文件缺失。"

    system_prompt = system_file.read_text(encoding="utf-8")
    user_tmpl = user_file.read_text(encoding="utf-8")

    # 4. 安全替换内容 (避免 .format() 因为内容中的 {} 报错)
    # 使用 replace 替代 format 更加安全
    user_content = user_tmpl.replace("{aggregated_content}", content)

    # 5. Token 长度简单预估 (字符数，非精确 token)
    if len(user_content) > 40000: # 粗略估计
        logger.warning("报告内容过长，可能触发模型上下文限制，正在截断...")
        user_content = user_content[:40000] + "\n\n(内容因过长被截断...)"

    try:
        logger.info(f"正在发送请求至模型: {model}...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2, # 降低随机性，保证报告严谨
            stream=False
        )
        return response.choices[0].message.content
    except openai.APIConnectionError as e:
        logger.error(f"网络连接失败: {e}")
        return "错误：无法连接到大模型服务，请检查网络。"
    except openai.AuthenticationError:
        logger.error("API Key 错误")
        return "错误：身份验证失败，请检查 API Key。"
    except Exception as e:
        logger.error(f"LLM 调用发生未知错误: {str(e)}")
        return f"AI 分析生成失败：{str(e)}"