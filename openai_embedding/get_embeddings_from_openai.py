import os
from loguru import logger
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
dotenv_path = '.env.local'
load_dotenv(dotenv_path=dotenv_path)

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