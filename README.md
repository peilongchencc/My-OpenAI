# openai_parse:

本文档基于OpenAI官网介绍，主要用于个人理解与API调用测试。<br>

**文件介绍:**<br>

- `fastapi_sse_example.py` : 异步方式实现fastapi调用OpenAI服务，结果以sse方式传输。

- `sanic_sse_example.py` : 异步方式实现Sanic调用OpenAI服务，结果以sse方式传输。

- `gradio_stream_openai.py` : 异步方式接收FastAPI或Sanic以sse方式传输的数据，然后以界面方式呈现。

- `openai_test.py`: 同步写法，支持终端直接测试openai效果。(前提:终端需能连接openai服务)

**OpenAI官网内容介绍:**<br>

- [openai\_parse:](#openai_parse)
  - [Key concepts(关键概念):](#key-concepts关键概念)
    - [Text generation models(文本生成模型):](#text-generation-models文本生成模型)
    - [Assistant:](#assistant)
    - [Embeddings(词嵌入):](#embeddings词嵌入)
    - [Tokens:](#tokens)
  - [Developer quickstart(开发者快速入门):](#developer-quickstart开发者快速入门)
    - [Get up and running with the OpenAI API(快速开始使用OpenAI API):](#get-up-and-running-with-the-openai-api快速开始使用openai-api)
    - [Account setup(账户设置):](#account-setup账户设置)
    - [API Keys:](#api-keys)
    - [Quickstart language selection(快速开始语言选择):](#quickstart-language-selection快速开始语言选择)
    - [Set your API key(设置你的 API 密钥):](#set-your-api-key设置你的-api-密钥)
      - [Seetup your API key for all projects(recommended)(为所有项目设置你的 API 密钥)(推荐):](#seetup-your-api-key-for-all-projectsrecommended为所有项目设置你的-api-密钥推荐)
      - [Setup your API key for a single project(为单个项目设置你的 API 密钥):](#setup-your-api-key-for-a-single-project为单个项目设置你的-api-密钥)
    - [Sending your first API request(发送你的第一个API请求):](#sending-your-first-api-request发送你的第一个api请求)
      - [chatcompletions(聊天补全):](#chatcompletions聊天补全)
      - [Embedding:](#embedding)
      - [images:](#images)
    - [chatcompletions with dotenv:](#chatcompletions-with-dotenv)
      - [unstreaming(非流式输出):](#unstreaming非流式输出)
      - [streaming(流式输出):](#streaming流式输出)
      - [multi\_turn\_dialogue(多轮对话):](#multi_turn_dialogue多轮对话)
      - [异步方式调用--官方示例:](#异步方式调用--官方示例)
      - [异步方式调用--使用dotenv的简单示例:](#异步方式调用--使用dotenv的简单示例)
      - [API中的system、user、assistant作用解析:](#api中的systemuserassistant作用解析)
    - [Next steps(接下来的步骤):](#next-steps接下来的步骤)
  - [settings:](#settings)
    - [Billing settings(账单设置):](#billing-settings账单设置)

"Head to chat.openai.com."：这部分是一个建议或指令，意思是“前往 chat.openai.com。”。“Head to”是一个常用的英语短语，用来建议某人去某个地方。在这里，它意味着如果你想使用或了解更多关于ChatGPT的信息，应该访问网址“chat.openai.com”，这是一个特定的网站链接。<br>

Explore the API(探索这个应用程序编程接口 (API))<br>

[Watch the first OpenAI Developer Day keynote(观看首届 OpenAI 开发者日主题演讲)](https://youtu.be/U9mJuUkhUzk)

> OpenAI Developer Day:指的是由 OpenAI 组织的一个开发者日活动。
> keynote: 这个词在这里指的是某个会议或活动中的主要演讲或主题演讲。通常，这种演讲由重要人物进行，旨在阐述会议的主要主题或传达重要信息。

The OpenAI API can be applied to virtually any task. We offer a range of models with different capabilities and price points, as well as the ability to fine-tune custom models.

OpenAI API 实际上可以应用于任何任务。我们提供一系列具有不同功能和价格点的模型，以及微调定制模型的能力。


🚨🚨🚨Note:<br>

----

你可以在使用 openAI API 的过程中见到以下图片:

![](./materials/uasge_limit.jpg)

这是提醒你:

你已达到使用限额。欲了解更多详情，请查看你的使用仪表板和账单设置。如果你还有其他问题，请通过我们的帮助中心 help.openai.com 与我们联系。

----


## Key concepts(关键概念):

### Text generation models(文本生成模型):

OpenAI's text generation models (often referred to as generative pre-trained transformers or "GPT" models for short), like GPT-4 and GPT-3.5, have been trained to understand natural and formal(正式的) language. Models like GPT-4 allows text outputs in response to their inputs. **The inputs to these models are also referred to as "prompts".** Designing a prompt is essentially(本质上) how you "program" a model like GPT-4, usually by providing instructions(指令) or some examples of how to successfully complete a task. Models like GPT-4 can be used across a great variety of tasks including content or code generation, summarization, conversation, creative writing(创意写作), and more. Read more in our introductory text generation guide and in our prompt engineering guide.<br>

OpenAI的文本生成模型（通常被称为生成式预训练transformers，简称“GPT”模型），比如GPT-4和GPT-3.5，已被训练以理解自然语言和正式语言。像GPT-4这样的模型可以根据输入生成文本输出。**这些模型的输入也被称为“提示”**。设计一个提示本质上就是如何“编程”一个像GPT-4这样的模型，通常是通过提供指令或一些示例来展示如何成功完成一个任务。像GPT-4这样的模型可以应用于广泛的任务，包括内容或代码生成、摘要、对话、创意写作等等。欲了解更多，请阅读我们的入门文本生成指南和提示工程指南。<br>

### Assistant:

Assistants refer to entities, which in the case of the OpenAI API are powered by large language models like GPT-4, that are capable of performing(执行) tasks for users. These assistants operate based on the instructions(指令) embedded within the context window of the model. They also usually have access to tools which allows the assistants to perform more complex tasks like running code or retrieving(检索) information from a file. Read more about assistants in our Assistants API Overview.<br>

Assistants是指由大型语言模型（如 GPT-4）驱动的实体，在 OpenAI API 的情况下，这些Assistants能够为用户执行任务。这些Assistants的运作基于嵌入在模型的上下文窗口中的指令。它们通常还可以访问工具，使Assistants能夠执行更复杂的任务，如运行代码或从文件中检索信息。欲了解更多关于Assistants的信息，请阅读我们的Assistants API 概览。<br>

### Embeddings(词嵌入):

An embedding is a vector representation(表示) of a piece of data (e.g. some text) that is meant to preserve(保留) aspects(方面) of its content and/or its meaning. Chunks of data(数据块) that are similar in some way will tend(趋向) to have embeddings that are closer together than unrelated data. OpenAI offers text embedding models that take as input a text string and produce as output an embedding vector. Embeddings are useful for search, clustering, recommendations, anomaly(异常) detection, classification, and more. Read more about embeddings in our embeddings guide.<br>

Embedding是一种数据（例如某些文本）的向量表示形式，旨在保留其内容和/或含义的某些方面。在某种程度上相似的数据块，其embedding通常会比不相关数据的embedding更为接近。OpenAI提供了文本embedding模型，这些模型以文本字符串作为输入，并产生embedding向量作为输出。Embedding对于搜索、聚类、推荐、异常检测、分类等领域非常有用。想了解更多关于embedding的信息，请阅读我们的embedding指南。<br>

### Tokens:

Text generation and embeddings models process text in chunks called tokens. Tokens represent commonly occurring sequences of characters. For example, the string " tokenization" is decomposed(分解) as " token" and "ization", while a short and common word like " the" is represented as a single token. **Note that in a sentence, the first token of each word typically starts with a space character.** Check out our tokenizer tool(分词工具) to test specific strings and see how they are translated into tokens. As a rough rule of thumb, 1 token is approximately(大概) 4 characters(字符) or 0.75 words for English text.<br>

> "thumb" 在英语中的字面意思是“拇指”。但在这个上下文中，"rule of thumb" 是一个成语，意思是“经验法则”或“粗略的估计方法”。

文本生成和Embeddings模型通过被称为 tokens 的单元来处理文本。Tokens 代表常见的字符序列。例如，字符串 " tokenization" 被拆分为 " token" 和 "ization"，而像 " the" 这样短小且常见的单词则被表示为一个单独的 token。**请注意，在一个句子中，每个单词的第一个 token 🤨**你可以查看我们的分词工具，测试特定字符串，并查看它们是如何被转换为 tokens 的。作为一个粗略的经验法则，对于英文文本来说，1个 token 大约相当于4个字符或0.75个单词。<br>


## Developer quickstart(开发者快速入门):

### Get up and running with the OpenAI API(快速开始使用OpenAI API):

> “Get up and running” 是一个常用的英语短语，意思是迅速开始或迅速投入到某事中。字面上，“get up”意味着起身或起立，但在这里它更多地表达的是开始行动或启动的意思。

The OpenAI API provides a simple interface for developers(开发者) to create an intelligence layer(智能层) in their applications, powered by OpenAI's **state of the art(最先进的)** models. The Chat Completions(完成) endpoint powers ChatGPT and provides a simple way to take text as input and use a model like GPT-4 to generate an output.<br>

OpenAI的API为开发者提供了一个简单的接口，用于在他们的应用程序中创建一个由OpenAI最先进的模型驱动的智能层。Chat Completions端点驱动了ChatGPT，并提供了一种简单的方式，即接受文本输入，并使用像GPT-4这样的模型来生成输出。<br>

This quickstart is designed to help get your local development environment setup(设置；搭建) and send your first API request(请求). If you are an experienced(经验丰富的) developer or want to just dive into("深入研究";"迅速投入") using the OpenAI API, the API reference of GPT guide are a great place to start. Throughout this quickstart, you will learn:<br>

这份快速入门旨在帮助你搭建本地开发环境并发送你的首个API请求。如果你是一位经验丰富的开发者，或者想直接深入使用OpenAI API，那么**GPT指南中的API参考文档**是一个绝佳的起点。在这份快速入门中，你将学习：<br>

- How to setup your development environment(如何搭建你的开发环境)
- How to install the latest SDKs(如何安装最新的SDK)
- Some of the basic concepts of the OpenAI API(OpenAI API的一些基本概念)
- How to send your first API request(如何发送你的首个API请求)

If you run into any challenges or have questions getting started, please join our developer forum(论坛).<br>

如果在开始过程中遇到任何挑战或有问题，请加入我们的开发者论坛。<br>

### Account setup(账户设置):

First, create an OpenAI account or sign in. Next, navigate(前往；导航至) to the [API key page](https://platform.openai.com/api-keys) and "Create new secret key", optionally(可选) naming the key. Make sure to save this somewhere safe and do not share it with anyone.<br>

首先，创建一个OpenAI账户或登录。接着，前往❤️**API密钥页面**并“创建新的密钥”，可以选择为密钥命名。确保将其保存在安全的地方，并且不要与任何人分享。<br>


### API Keys:

Your secret API keys are listed below. Please note that **🚨we do not display your secret API keys again🚨** after you generate them.<br>

你的 `secret API keys` 如下所列。请注意，一旦你生成这些密钥，我们将不会再次显示它们。<br>

Do not share your API key with others, or expose(暴露) it in the browser(浏览器) or other client-side(客户端) code. In order to protect the security of your account, OpenAI may also automatically(自动地) disable(使无效) any API key that we've found has leaked(泄漏) publicly.<br>

> "client-side"表示客户端，服务器端为 "server-side"。

请不要与他人共享你的 API 密钥，也不要在浏览器或其他客户端代码中暴露它。为了保护你账户的安全，一旦发现有 API 密钥被公开泄露，OpenAI 可能会自动禁用该密钥。<br>

Enable tracking(追踪) to see usage per API key on the Usage page.<br>

在 **Usage** 页面上启用追踪功能，以查看每个 API 密钥的使用情况。<br>

| NAME                  | SECRET KEY | TRACKING | CREATED     | LAST USED  |
|-----------------------|------------|----------|-------------|------------|
| peilongchencc_openai  | sk-...eZeu | Enable   | 2023年6月8日 | 2023年6月8日 |

> “TRACKING”列中的“Enable”意思是“启用”。在这里，它表示对该 API 密钥的使用情况进行追踪功能是开启的。这意味着你可以在“使用情况”页面查看到这个特定 API 密钥的使用详情，比如调用次数、使用频率等信息。这个功能对于监控和分析 API 密钥的使用情况非常有用，特别是当你想确保密钥没有被滥用时。

Default organization(默认组织)<br>

If you belong to multiple(多个) organizations, this setting controls which organization is used by default when making requests with the API keys above.<br>

如果你属于多个组织，此设置将控制在使用上述 API 密钥进行请求时默认使用哪个组织。<br>

Note: You can also specify which organization to use for each API request. See Authentication to learn more.<br>

备注：你也可以为每个 API 请求指定使用哪个组织。请参阅“身份验证”了解更多信息。<br>

### Quickstart language selection(快速开始语言选择):

Select the tool or language(这里由下文可知指的是编程语言) you want to get started using the OpenAI API with.<br>

请选择你希望使用 OpenAI API 开始使用的工具或编程语言。<br>

Python is a popular programming language that is commonly(通常地) used for data applications, web development(网页开发), and many other programming tasks due to its ease of use. OpenAI provides a custom(定制的) Python library which makes working with the OpenAI API in Python simple and efficient.<br>

> "custom" 表示 "定制的"，"自定义的"在英语中通常可以表达为 "customized" 或 "personalized"。例如，"customized computer" 或 "personalized plan" 分别表示“定制的电脑”和“个性化的计划”。

Python 是一种流行的编程语言，因其易用性，常用于数据应用、网页开发和许多其他编程任务。OpenAI 提供了一个定制的 Python 库，使得在 Python 中使用 OpenAI API 变得简单高效。<br>

### Set your API key(设置你的 API 密钥):

#### Seetup your API key for all projects(recommended)(为所有项目设置你的 API 密钥)(推荐):

The main advantage to making your API key accessible for all projects is that the Python library will automatically detect(检测) it and use it without having to write any code.<br>

将你的 API 密钥设置为对所有项目可访问的主要优势在于，Python 库将自动检测并使用它，无需编写任何代码。<br>

> 由于笔者使用的是mac，惯用的也是Linux系统，所以这里只介绍mac的操作方式，windows不做介绍。

Open Terminal: You can find it in the Applications folder or search for it using Spotlight (Command + Space).<br>

打开终端：你可以在“应用程序”文件夹中找到它，或使用 Spotlight（Command + Space）进行搜索。<br>

Edit Bash Profile: Use the command `nano ~/.bash_profile` or `nano ~/.zshrc` (for newer MacOS versions) to open the profile file in a text editor.<br>

编辑 Bash 配置文件：使用命令 `nano ~/.bash_profile` 或 `nano ~/.zshrc`（适用于较新的 MacOS 版本）在文本编辑器中打开配置文件。<br>

> 如果你习惯vim指令，vim指令更方便。
> 如果你不清楚你用的哪种shell环境，可终端运行 `echo $SHELL` 指令进行查看，终端应该会输出类似 `/bin/zsh` 的结果。

Add Environment Variable: In the editor, add the line below, replacing `your-api-key-here` with your actual(实际的) API key:<br>

添加环境变量：在编辑器中，添加下面的这行代码，将 `your-api-key-here` 替换为你实际的 API 密钥：<br>

```bash
export OPENAI_API_KEY='your-api-key-here'
```

Save and Exit: Press **Ctrl+O** to write the changes, followed by **Ctrl+X** to close the editor.<br>

保存并退出：按 **Ctrl+O** 保存更改，然后按 **Ctrl+X** 关闭编辑器。<br>

Load Your Profile: Use the command `source ~/.bash_profile` or `source ~/.zshrc` to load the updated profile.<br>

加载你的配置文件：使用命令 `source ~/.bash_profile` 或 `source ~/.zshrc` 加载更新后的配置文件。<br>

Verification: Verify the setup by typing `echo $OPENAI_API_KEY` in the terminal. It should display your API key.<br>

验证：在终端中输入 `echo $OPENAI_API_KEY` 进行验证。它应该会显示你的 API 密钥。<br>

#### Setup your API key for a single project(为单个项目设置你的 API 密钥):

If you only want your API key to be accessible(易于获得或使用的) to a single project, you can create a local `.env` file which contains the API key and then explicitly(明确地;直接地) use that API key with the Python code shown in the steps to come.<br>

如果你只希望你的API密钥被单个项目访问，你可以在项目文件夹中创建一个本地的 `.env` 文件，其中包含API密钥，然后在接下来的步骤中明确地在Python代码中使用这个API密钥。<br>

Start by going to the project folder you want to create the `.env` file in.<br>

首先，前往你想要创建 `.env` 文件的项目文件夹。<br>

Note: In order for your `.env` file to be ignored by version control, create a `.gitignore` file in the root of your project directory. Add a line with `.env` on it which will make sure your API key or other secrets are not accidentally(意外地) shared via version control.<br>

注意：为了让你的 `.env` 文件被版本控制忽略，请在你的项目根目录下创建一个 `.gitignore` 文件。在文件中加入一行包含.env的内容，这将确保你的API密钥或其他敏感信息不会通过版本控制意外分享。<br>

Once you create the `.gitignore` and `.env` files using the terminal or an integrated(集成的) development environment (IDE), copy your secret API key and set it as the `OPENAI_API_KEY` in your `.env` file. If you haven't created a secret key yet, you can do so on the API key page.<br>

一旦你使用终端或集成开发环境（IDE）创建了 `.gitignore` 和 `.env` 文件，复制你的秘密API密钥，并将其设置为.env文件中的OPENAI_API_KEY。如果你还没有创建秘密密钥，你可以在API密钥页面上进行创建。<br>

The `.env` file should look like the following:<br>

`.env` 文件应该如下所示：<br>

```txt
# Once you add your API key below, make sure to not share it with anyone! The API key should remain private.
# 添加你的API密钥后，请确保不与任何人分享！API密钥应保持私密。
OPENAI_API_KEY=abc123
```

The API key can be imported by running the code below:<br>

可以通过运行以下代码导入API密钥：

```python
from openai import OpenAI

client = OpenAI()

# defaults to getting the key using os.environ.get("OPENAI_API_KEY")
# if you saved the key under a different environment variable name, you can do something like:

# 默认通过os.environ.get("OPENAI_API_KEY")获取密钥
# 如果你在不同的环境变量名下保存了密钥，你可以这样做：

# client = OpenAI(
#   api_key=os.environ.get("CUSTOM_ENV_NAME"),
# )
```

### Sending your first API request(发送你的第一个API请求):

After you have Python configured and an API key setup, the final step is to send a request to the OpenAI API using the Python library. To do this, create a file named `openai-test.py` using th terminal or an IDE.<br>

在配置好 Python 并设置好 API 密钥之后，最后一步是使用 Python 库向 OpenAI API 发送请求。为此，请使用终端或集成开发环境创建一个名为 `openai-test.py` 的文件。<br>

Inside the file, copy and paste one of the examples below:<br>

在文件中，复制并粘贴以下示例之一：<br>

#### chatcompletions(聊天补全):

```python
from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)

print(completion.choices[0].message)
```

To run the code, enter `python openai-test.py` into the terminal / command line.<br>

要运行代码，请在终端/命令行中输入 `python openai-test.py`。<br>

The Chat Completions example highlights(突出显示；强调) just one area of strength(力量；强项) for our models: creative ability. Explaining recursion(递归) (the programming topic) in a well formatted poem is something both the best developers and best poets(诗人) would struggle with. In this case, gpt-3.5-turbo does it effortlessly.<br>

“聊天补全”示例只展示了我们模型的一个强项：创造力。用格式良好的诗歌解释递归（编程话题）是即使最优秀的开发者和诗人也会感到困难的事情。而在这个例子中，**gpt-3.5-turbo** 轻松地做到了。<br>

> "Turbo" 这个词最初来源于“涡轮增压器（turbocharger）”，是一种用于提升发动机效能的装置。在更广泛的用法中，“turbo”通常用来形容某事物具有快速、高效或强大的性质。例如，在科技和软件领域，"turbo" 通常用来表示某个版本或型号具有更快的处理速度、更高的性能或更先进的功能。在上文提到的 "gpt-3.5-turbo" 中，"turbo" 用来指代该模型的高效率或高性能特点。

#### Embedding:

```python
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
  model="text-embedding-ada-002",
  input="The food was delicious and the waiter..."
)

print(response)
```

#### images:

```python
from openai import OpenAI
client = OpenAI()

response = client.images.generate(
  prompt="A cute baby sea otter",
  n=2,
  size="1024x1024"
)

print(response)
```

### chatcompletions with dotenv:

In this section, we will introduce how to use `dotenv` to load the `OPENAI_API_KEY`, and demonstrate(展示；证明) how to test it using chat completions.<br>

在这里介绍使用`dotenv`加载`OPENAI_API_KEY`，并调用chatcompletions进行测试。<br>

#### unstreaming(非流式输出):

```python
"""
@author:ChenPeilong(peilongchencc@163.com)
@description:OpenAI unstreaming output example code.
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

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY"),
)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)

print(completion.choices[0].message)
print(type(completion.choices[0].message))  # <class 'openai.types.chat.chat_completion_message.ChatCompletionMessage'>
# only content
print(completion.choices[0].message.content)
```

#### streaming(流式输出):

```python
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

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY"),
)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ],
  stream=True
)

for chunk in completion:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

#### multi_turn_dialogue(多轮对话):

```python
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
```

#### 异步方式调用--官方示例:

OpenAI官方提供了异步方式调用的示例代码，参考网址如下:<br>

```txt
https://github.com/openai/openai-python/blob/9e6e1a284eeb2c20c05a03831e5566a4e9eaba50/README.md
```

具体代码如下:<br>

```python
import os
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


async def main() -> None:
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-3.5-turbo",
    )


asyncio.run(main())
```

#### 异步方式调用--使用dotenv的简单示例:

```python
import os
import asyncio
from loguru import logger
from dotenv import load_dotenv
import openai

# 加载环境变量
dotenv_path = '.env.local'
load_dotenv(dotenv_path=dotenv_path)

# 设置日志
logger.remove()
logger.add("openai_stream.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")

async def main():
    client = openai.AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    completion = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
            {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
        ],
        stream=True
    )

    async for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")

# 运行异步主函数
if __name__ == "__main__":
    asyncio.run(main())
```

#### API中的system、user、assistant作用解析:

- system: 它设定了 AI 的行为、角色、和背景，或者你可以理解为语境。常常用于开始对话，给出一个对话的大致方向，或者设置对话的语气和风格。

ChatGPT网页端不显示system选项，你需要用`user`角色给予它定义。例如，输入："你是一个助理"或"你是一名历史教师"。这个消息可以帮助设定对话的语境，以便 AI 更好地理解其在对话中的角色。<br>

- assistant:即系统回复的内容，在使用 API 的过程中，你不需要直接生成 assistant 消息，因为它们是由 API 根据 system 和 user 消息自动生成的。

- user:就是我们输入的问题或请求。比如说"请给我一份使用python读取json文件的示例代码"

### Next steps(接下来的步骤):

Now that you have made you first OpenAI API request, it is time to explore what else is possible:<br>

既然你已经完成了首次OpenAI API请求，现在是时候探索更多可能性了：<br>

- For more detailed information on our models and the API, see our [GPT guide](https://platform.openai.com/docs/guides/text-generation).(想要了解我们的模型和API的更多详细信息，请查看我们的GPT指南。)

- Visit the [OpenAI Cookbook](https://cookbook.openai.com/) for in-depth example API use-cases, as well as code snippets for common tasks.(访问OpenAI食谱，了解深入的API使用案例以及常见任务的代码片段。)

- Wondering what OpenAI's models are capable of? Check out our library of [example prompts](https://platform.openai.com/examples).(想知道OpenAI的模型能做什么？查看我们的示例提示库。)

- Want to try the API without writing any code? Start experimenting in the [Playground](https://platform.openai.com/playground).(想不编写任何代码就尝试API？开始在Playground实验。)

- Keep our [usage policies](https://openai.com/policies/usage-policies) in mind as you start building.(开始构建时，请牢记我们的使用政策。)

## settings:

### Billing settings(账单设置):

Note: This does not reflect the status of your ChatGPT account.<br>

备注：这并不反映你的ChatGPT账户的状态。<br>