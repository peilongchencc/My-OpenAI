"""
Description: openai读取本地图片代码示例。
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

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("env_config/.env.local")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 将图片编码为base64
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

image_path = "docs/FizdHLbjxY.jpg"
# 获取 base64 string
base64_image = encode_image(image_path)

response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "请帮我提取出图片中的内容"},
        {
          "type": "image_url",  
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}",
            "detail": "high"
          },
        },
      ],
    }
  ],
  max_tokens=300,
)

print(response.choices[0].message.content)