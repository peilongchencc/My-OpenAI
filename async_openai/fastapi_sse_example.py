"""
@author:ChenPeilong(peilongchencc@163.com)
@description:OpenAI streaming output example code with fastapi.
"""
import os
import json
from loguru import logger
from dotenv import load_dotenv
from openai import AsyncOpenAI
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI()

# 加载环境变量
dotenv_path = '.env.local'
load_dotenv(dotenv_path=dotenv_path)

# 设置日志
logger.remove()
logger.add("openai_stream.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")


async def get_openai_response(chat_history):
    async with AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")) as client:
        completion = await client.chat.completions.create(
            # model="gpt-3.5-turbo",
            model="gpt-4-0125-preview",
            messages=chat_history,
            stream=True
        )
        async for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                # print(chunk.choices[0].delta.content, end="") # 终端打印
                yield chunk.choices[0].delta.content    # 常规返回方式，适用于gradio
                # yield f"data:{chunk.choices[0].delta.content}\n\n"  # 标准sse响应需要的格式，适用于postman测试

@app.post("/chat")
async def chat(user_input: str = Form(...), chat_history: str = Form(...)):
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
        chat_response = get_openai_response(user_history)  # 无需await，因为StreamingResponse会处理异步迭代器
        return StreamingResponse(chat_response, media_type="text/event-stream")  # 使用StreamingResponse返回
    except ValueError as ve:
        logger.error(f"无效输入：{ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"处理聊天请求时发生错误：{e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8848)