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

# 获取当前设置的HTTP和HTTPS代理
http_proxy = os.getenv('http_proxy') or "未设置"
https_proxy = os.getenv('https_proxy') or "未设置"

# 打印代理信息
print(f"当前HTTP代理: {http_proxy}")
print(f"当前HTTPS代理: {https_proxy}")
