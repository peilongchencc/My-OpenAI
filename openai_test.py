"""
@author:ChenPeilong(peilongchencc@163.com)
@description:OpenAI streaming output example code.
"""
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


def get_openai_response(chat_history):
    # create openAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # connect openai API server and fetch the response of chat_history with streaming.
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=chat_history,
        stream=True
    )
    # combine the results of streaming output.
    response_content = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
            response_content += chunk.choices[0].delta.content
    print() # For Line Breaks, Optimizing Terminal Display.
    chat_history.append({"role": "assistant", "content": response_content})
    return chat_history

if __name__ == '__main__':
    # chath_istory can be [], without providing a semantic context(语义环境).
    # chat_history = [{"role": "system", "content": "你是一名NLP算法工程师"}]
    chat_history = []
    while True:
        user_input = input("\nPlease enter your question (type 'exit' to end the program):")
        print() # For Line Breaks, Optimizing Terminal Display.
        # If the user enters 'exit', then terminate the loop.
        if user_input == 'exit':
            break
        
        chat_history.append({"role": "user", "content": user_input})
        # fetch the results of the API response and display them in a streaming manner on the terminal, 
        # while simultaneously(同时) updating chat_history.
        chat_history = get_openai_response(chat_history)