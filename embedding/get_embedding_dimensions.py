"""
Description: openai词向量获取示例。
Notes: 
"""
import sys
import os

# 获取当前脚本的绝对路径
current_script_path = os.path.abspath(__file__)
# 获取当前脚本的父目录的父目录
parent_directory_of_the_parent_directory = os.path.dirname(os.path.dirname(current_script_path))
# 将这个目录添加到 sys.path
sys.path.append(parent_directory_of_the_parent_directory)

from loguru import logger
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv('env_config/.env.local')

# 设置日志
logger.remove()
logger.add("openai_stream.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.embeddings.create(
    input="《老人与海》这篇文章被选入了小学语文课本。",
    model="text-embedding-3-small",
    dimensions=768
)

print(response.data[0].embedding)

# type(response.data[0].embedding)
# <class 'list'>
# len(response.data[0].embedding)
# 1536