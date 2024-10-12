"""
Description: 以python sdk方式调用openai chat服务示例。
Notes: 
"""
import os
from dotenv import load_dotenv
# 环境变量必须要在使用环境变量中配置前导入
load_dotenv("env_config/.env.local")

# 设置网络代理环境变量
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'

from openai import OpenAI
client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

completion = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "你有什么功能？"}
  ]
)

print(completion.choices[0].message)
