# OpenAI Vision

本章介绍使用大模型与图片进行交互，例如用户上传一张图片，并提问 "图片中有什么？"，大模型会分析图片然后返回结果。<br>
- [OpenAI Vision](#openai-vision)
  - [传输方式:](#传输方式)
  - [代码示例:](#代码示例)
    - [传递图片链接示例:](#传递图片链接示例)
    - [传递base64编码的图片示例:](#传递base64编码的图片示例)
    - [Notes:](#notes)
  - [模型局限性:](#模型局限性)
  - [参数解释:](#参数解释)
  - [FAQ (Frequently Asked Questions):](#faq-frequently-asked-questions)
    - [为什么要将图片转化为base64编码格式？](#为什么要将图片转化为base64编码格式)


## 传输方式:

Images are made available to the model in two main ways: by passing a link to the image or by passing the base64 encoded image directly in the request.<br>

图片可以通过两种主要方式提供给模型：通过传递图片链接或在请求中直接传递base64编码的图片。<br>


## 代码示例:

### 传递图片链接示例:

```python
"""
Description: openai读取远程链接型图片代码示例。
Notes: 
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("env_config/.env.local")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "What’s in this image?"},
        {
          "type": "image_url",
          "image_url": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            "detail": "high"
          },
        },
      ],
    }
  ],
  max_tokens=300,
)

print(response.choices[0].message.content)
```

### 传递base64编码的图片示例:

```python
"""
Description: openai读取本地图片代码示例。
Notes: 
"""
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

image_path = "FizdHLbjxY.jpg"
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
```

### Notes:

The model is best at answering general questions about what is present in the images.<br>

该模型最擅长回答有关图像中存在的事物的一般问题。<br>

While it does understand the relationship between objects in images, it is not yet optimized to answer detailed questions about the location of certain objects in an image.<br>

虽然它确实理解图像中对象之间的关系，但尚未针对回答有关图像中某些对象位置的详细问题进行优化。<br>

For example, you can ask it what color a car is or what some ideas for dinner might be based on what is in your fridge, but if you show it an image of a room and ask it where the chair is, it may not answer the question correctly.<br>

例如，你可以问它车是什么颜色的，或者根据冰箱里的物品询问晚餐的建议，但如果你给它看一张房间的图像并问椅子在哪里，它可能无法正确回答这个问题。<br>

It is important to keep in mind the limitations of the model as you explore what use-cases visual understanding can be applied to. <br>

在探索视觉理解可以应用于哪些用例时，牢记该模型的局限性是很重要的。<br>


## 模型局限性:

虽然具备视觉功能的 GPT-4 功能强大，可以用于许多场景，但理解其局限性非常重要。以下是了解到的一些局限性：<br>

- 医疗影像：该模型不适用于解释专业的医疗影像，如 CT 扫描，也不应该用于医疗建议。

- 非英文：该模型在处理含有非拉丁字母文本的图像时，可能表现不佳，例如日文或韩文。

- 小文本：放大图像中的文本以提高可读性，但避免裁剪掉重要细节。

- 旋转：该模型可能会误解旋转或倒置的文本或图像。

- 视觉元素：该模型可能难以理解图表或颜色和样式（如实线、虚线或点线）变化的文本。

- 空间推理：该模型在需要精确空间定位的任务中表现不佳，例如识别国际象棋位置。

- 准确性：在某些情况下，该模型可能生成不准确的描述或字幕。

- 图像形状：该模型在处理全景和鱼眼图像时表现不佳。

- 元数据和调整大小：该模型不会处理原始文件名或元数据，图像在分析前会被调整大小，影响其原始尺寸。

- 计数：可能对图像中的物体数量进行大致估计。

**🚨笔者使用过程中的经验:**<br>

利用gpt vision做OCR的效果不理想，推测训练方式为 "图A <--pair--> 图A的描述性文本"，所以用户询问类似 "图中有哪些内容？" 的问题时效果好，但询问 "请帮我将图片中的文本提取出来" 效果不理想。<br>


## 参数解释:

By controlling the `detail` parameter, which has three options, `low`, `high`, or `auto`, you have control over how the model processes the image and generates its textual understanding.<br>

通过控制细节参数，该参数有三个选项：`low`、`high`或`auto`，您可以控制模型如何处理图像并生成其文本理解。<br>

By default, the model will use the `auto` setting which will look at the image input size and decide if it should use the `low` or `high` setting.<br>

默认情况下，模型将使用 `auto` 设置，该设置将查看图像输入大小并决定是否应使用 `low` 或 `high` 设置。<br>

🔥`low` will enable the "low res" mode. / `low` 将启用“低分辨率”模式。<br>

The model will receive a low-res 512px x 512px version of the image, and represent the image with a budget of 85 tokens.<br>

模型将接收一个低分辨率的512px x 512px版本的图像，并使用85个标记来表示图像。<br>

This allows the API to return faster responses and consume fewer input tokens for use cases that do not require high detail.<br>

这使API能够在不需要高细节的用例中返回更快的响应并消耗更少的输入标记。<br>

🔥`high` will enable "high res" mode, which first allows the model to first see the low res image (using 85 tokens) and then creates detailed crops using 170 tokens for each 512px x 512px tile.<br>

`high`将启用“高分辨率”模式，该模式首先允许模型看到低分辨率图像（使用85个标记），然后为每个512px x 512px的图块使用170个标记创建详细的裁剪。<br>


## FAQ (Frequently Asked Questions): 

### 为什么要将图片转化为base64编码格式？

将本地图像转化为base64编码格式是为了在HTTP请求中发送图像数据。HTTP请求通常是以文本格式发送的，base64编码是一种常见的方法，可以将二进制数据（如图像）转化为文本格式，以便嵌入到请求中。<br>