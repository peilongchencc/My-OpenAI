"""
Author: peilongchencc@163.com
Description: 
Requirements: 异步方式接收FastAPI或Sanic以sse方式传输的数据,然后以界面方式呈现。
Reference Link: 
Notes: 
"""
import json
import aiohttp
import gradio as gr
from loguru import logger

# 设置日志
logger.remove()
logger.add("baidu_llm_gradio.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")

async def predict(message, history):
    chat_history = json.dumps(history)  # history的数据类型为列表嵌套列表
    # 设置llm服务接口
    URL = 'http://localhost:8848/chat'
    # 设置传给llm服务接口的参数
    DATA = {
        # 'user_id': 'peilongchencc',
        'user_input': message,
        'chat_history': chat_history
    }

    try:
        async with aiohttp.ClientSession() as session:  # 创建ClientSession
            async with session.post(URL, data=DATA) as response:  # 异步发送POST请求
                generated = ""  # 用于存储之前生成的字符
                async for chunk in response.content.iter_any():
                    decoded_chunk = chunk.decode('utf-8')   # chunk为字节类型，需要采用`utf-8`转为可识别内容。
                    generated += decoded_chunk  # 将新字符添加到存储的字符串中
                    yield generated
    except aiohttp.ClientError as e:
        logger.error(f"网络请求错误: {e}")
        yield "对不起，发生了网络错误。"

demo = gr.ChatInterface(
    fn=predict,
    chatbot=gr.Chatbot(height=500),
    textbox=gr.Textbox(placeholder="Ask me a question...", container=False, scale=7),
    title="Dragon Chatbot",
    description="Ask Dragon Chatbot any question",
    theme="soft",
    examples=["Hello", "请给我一份读取json文件的python代码", "\"consist\"的中文含义是什么？"],
    cache_examples=True,
    retry_btn=None,
    undo_btn="删除上一轮对话",
    clear_btn="清空历史数据",
    concurrency_limit=10
).queue()

demo.launch(server_name="0.0.0.0")  # 开放公网访问，否则默认绑定到本地IP（127.0.0.1）上，仅允许本机访问。
# demo.launch(server_name="0.0.0.0", server_port=8866) # 如果你想要修改端口号，可以使用该示例
