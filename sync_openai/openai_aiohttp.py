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
dotenv_path = '.env.local'
load_dotenv(dotenv_path=dotenv_path)

# 设置日志
logger.remove()
logger.add("openai_stream.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def fetch_openai_completion():
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "你是一名半导体方向的专家。"
            },
            {
                "role": "user",
                "content": "在光路中，AMP是什么器件？"
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

# 使用 asyncio.run() 直接运行异步函数
asyncio.run(fetch_openai_completion())
