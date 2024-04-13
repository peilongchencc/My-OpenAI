"""
Author: peilongchencc@163.com
Description: 
Requirements: 异步方式实现Sanic调用OpenAI服务,结果以sse方式传输。
Reference Link: 
Notes: 
"""
import os
import json
from sanic import Sanic
from loguru import logger
from dotenv import load_dotenv
from openai import AsyncOpenAI

app = Sanic("my_app")

# 加载环境变量
dotenv_path = '.env.local'
load_dotenv(dotenv_path=dotenv_path)

# 设置日志
logger.remove()
logger.add("openai_stream.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")


async def get_openai_response(response, chat_history):
    """
    Args:
        response:Sanic response object.
    """
    async with AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")) as client:
        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_history,
            stream=True
        )
        async for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                await response.send(f"data:{chunk.choices[0].delta.content}\n\n")   # 标准sse响应需要的格式，适用于postman测试

@app.route("/ans", methods=["POST"])
async def answer(request):
    # fetch user's input.
    user_input = request.form.get("user_input")
    # fetch user's historical chat data.
    chat_history = request.form.get("chat_history") # string,such as '[]'
    response = await request.respond(content_type="text/event-stream")
    try:
        if not user_input:
            logger.warning("用户输入为空")
            raise ValueError("用户输入为空")

        # 因为传入的是json数据，需要解码
        chat_history = json.loads(chat_history)
        logger.info(f"当前对话历史为:\n{chat_history}\n 数据类型为:{type(chat_history)}")

        user_history = []   # 存储用户聊天信息
        # 如果历史聊天数据不为空
        if chat_history:
            for user_message, bot_message in chat_history:
                user_history.append({"role": "user", "content": user_message})
                user_history.append({"role": "assistant", "content": bot_message})
        # 前一步构成的user_history是偶数，这里需要加上当前输入，构成奇数的content
        user_history.append({"role": "user", "content": user_input})

        # 调用聊天API
        await get_openai_response(response, user_history)

    except Exception as e:
        logger.error(f"处理聊天请求时发生错误：{e}")
        raise f"处理聊天请求时发生错误：{e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8848)