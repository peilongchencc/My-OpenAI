"""
Description: 测试aiohttp方式连接openai服务。
Requirements: 
1. pip install aiohttp asyncio loguru python-dotenv
2. 创建`.env.local`文件,并填入配置。
Notes: 
1. 笔者使用的是URL形式连接,如果想要采用openai sdk的方式,可以自行修改代码。
2. 笔者使用的是异步,如果想要使用request(同步),请注意阻塞问题。
"""
import aiohttp
import asyncio
import os
from loguru import logger
from dotenv import load_dotenv

# 加载环境变量
dotenv_path = 'env_config/.env.local'
load_dotenv(dotenv_path=dotenv_path)

# 设置日志
logger.remove()
logger.add("openai_stream.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

data_info = """
请根据以下MySQL获取到的数据，针对用户输入进行回复。

MySQL中查询到的数据为:
|   employee_count |
|-----------------:|
|               15 |

用户输入: 请问我一共有几个员工？

回复要求:
1. 禁止回复类似 "根据您的查询结果" 的内容。
2. 如果markdown表格的形式呈现效果更好，请使用markdown表格的形式呈现。
"""

async def fetch_openai_completion():
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "gpt-4o",
        "messages": [
        #     {
        #         "role": "system",
        #         "content": "你是一名半导体方向的专家。"
        #     },
            {
                "role": "user",
                "content": data_info
            }
        ]
    }
    # 设置https代理--"http://127.0.0.1:7890"
    proxy = os.getenv("HTTPS_PROXY")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data, proxy=proxy) as response:
                logger.info("开始请求openai")
                response_text = await response.text()
                logger.info("openai返回内容")
                logger.info(f"Response from OpenAI: {response_text}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == '__main__':
    # 使用 asyncio.run() 直接运行异步函数
    asyncio.run(fetch_openai_completion())
