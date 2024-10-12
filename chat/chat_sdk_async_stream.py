"""
Description: 以python sdk方式调用openai chat服务示例。
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

from dotenv import load_dotenv
# 环境变量必须要在使用环境变量中配置前导入
load_dotenv("env_config/.env.local")

# 设置网络代理环境变量
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'

import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


async def main():
    completion = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一名体育老师"},
            {"role": "user", "content": "什么是最有效的减肥运动？"}
        ],
        stream=True
    )

    async for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")

# 运行异步主函数
if __name__ == "__main__":
    asyncio.run(main())