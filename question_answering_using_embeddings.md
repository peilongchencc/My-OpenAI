# question_answering_using_embeddings

文档中完整代码见 `question_answering_using_embeddings.py` 文件。<br>

- [question\_answering\_using\_embeddings](#question_answering_using_embeddings)
  - [Why search is better than fine-tuning(为什么搜索优于微调):](#why-search-is-better-than-fine-tuning为什么搜索优于微调)
  - [Search(搜索):](#search搜索)
  - [Full procedure(完整流程):](#full-procedure完整流程)
  - [Costs(成本):](#costs成本)
  - [Preamble(前言):](#preamble前言)
    - [Motivating example: GPT cannot answer questions about current events](#motivating-example-gpt-cannot-answer-questions-about-current-events)
  - [1. Prepare search data(准备搜索数据):](#1-prepare-search-data准备搜索数据)
  - [3. Ask(询问)](#3-ask询问)
  - [Example questions](#example-questions)
  - [Troubleshooting wrong answers](#troubleshooting-wrong-answers)
  - [More examples(更多)](#more-examples更多)
  - [知识拓展](#知识拓展)
    - [在NLP领域，什么因素决定了模型的输入长度？](#在nlp领域什么因素决定了模型的输入长度)
    - [为什么chatgpt可以用几千甚至几万长度的输入:](#为什么chatgpt可以用几千甚至几万长度的输入)
    - [HyDE技术是什么？](#hyde技术是什么)

GPT excels(擅长) at answering questions, but only on topics it remembers from its training data.<br>

GPT擅长回答问题，但仅限于它从训练数据中记住的话题。<br>

What should you do if you want GPT to answer questions about unfamiliar topics? E.g.<br>

如果你希望GPT回答关于不熟悉话题的问题该怎么办？例如：<br>

- Recent events after Sep 2021(2021年9月之后的最新事件，指GPT暂不含有的信息)

- Your non-public documents(你的非公开文档)

- Information from past conversations(过去对话中的信息)

- etc.(等等)

This notebook demonstrates(演示) a two-step Search-Ask method for enabling GPT to answer questions using a library of reference text.<br>

这个notebook演示了一种两步骤的搜索-询问方法，使GPT能够使用一库参考文本来回答问题。<br>

1. Search: search your library of text for relevant(相关的) text sections(搜索：搜索你的文本库，寻找相关的文本部分)

2. Ask: insert the retrieved(检索到的) text sections into a message to GPT and ask it the question(询问：将检索到的文本部分插入到消息中，然后向GPT提问)

## Why search is better than fine-tuning(为什么搜索优于微调):

GPT can learn knowledge in two ways(GPT可以通过两种方式学习知识):<br>

- Via model weights (i.e., fine-tune the model on a training set)(通过模型权重（即，在训练集上微调模型）)

- Via model inputs (i.e., insert the knowledge into an input message)(通过模型输入（即，将知识插入到输入消息中）)

Although fine-tuning can feel like the more natural option—training on data is how GPT learned all of its other knowledge, after all—we generally do not recommend it as a way to teach the model knowledge. Fine-tuning is better suited to teaching specialized tasks or styles, and is less reliable(可靠的) for factual recall.<br>

虽然微调感觉上可能是更自然的选择——**毕竟**，训练数据是GPT学习其所有其他知识的方式——我们通常不推荐它作为教授模型知识的方式。 **微调更适合教授专门的任务或风格，并且对于事实召回来说不太可靠。** 🚨🚨🚨<br>

As an analogy(类比；比喻), model weights are like long-term memory. When you fine-tune a model, it's like studying for an exam a week away. When the exam arrives, the model may forget details, or misremember facts it never read.<br>

作为一个类比，**模型权重就像是长期记忆**。当你对模型进行微调时，就像是为一周后的考试学习。当考试到来时，模型可能会忘记细节，或错记它从未阅读过的事实。<br>

In contrast(对比；对照), message inputs are like short-term memory. When you insert knowledge into a message, it's like taking an exam with open notes. With notes in hand, the model is more likely to arrive at correct answers.<br>

相比之下，**消息输入就像是短期记忆**。当你将知识插入到一条消息中时，就像是带着开放的笔记参加考试(**指开卷考试**)。手持笔记，模型更有可能得出正确的答案。<br>

One downside(负面；不利方面；缺点) of text search relative(相对的；也指相关的) to fine-tuning is that each model is limited by a maximum amount of text it can read at once:<br>

与微调相比，文本搜索的一个缺点是每个模型一次能读取的文本量有限：<br>

| Model        | Maximum text length       |
|--------------|---------------------------|
| gpt-3.5-turbo| 4,096 tokens (~5 pages)   |
| gpt-4        | 8,192 tokens (~10 pages)  |
| gpt-4-32k    | 32,768 tokens (~40 pages) |

(New model is available with longer contexts, `gpt-4-1106-preview` have 128K context window)<br>

新型号现已支持更长上下文，`gpt-4-1106-preview` 拥有 128K 上下文窗口。<br>

Continuing the analogy, you can think of the model like a student who can only look at a few pages of notes at a time, despite potentially having shelves of textbooks to draw upon.<br>

延续这个比喻，你可以将模型想象为一个学生，尽管可能有成架的教科书可以参考，但一次只能查看几页笔记。<br>

Therefore, to build a system capable of drawing upon large quantities of text to answer questions, we recommend using a Search-Ask approach.<br>

因此，为了构建一个能够利用大量文本来回答问题的系统，我们推荐使用搜索-询问（Search-Ask）方法。<br>

## Search(搜索):

Text can be searched in many ways. E.g.,(文本可以通过多种方式进行搜索，例如：)<br>

- Lexical-based search(基于词汇的搜索，Lexical表示词汇；词法)

- Graph-based search(基于图的搜索)

- Embedding-based search(基于词向量的搜索)

This example notebook uses embedding-based search. Embeddings are simple to implement and work especially well with questions, as questions often don't lexically overlap(重叠) with their answers.<br>

本示例notebook使用基于词向量的搜索方式。Embeddings简单易行，尤其适用于问题搜索，因为问题的文字往往与其答案不直接重叠。<br>

Consider embeddings-only search as a starting point for your own system. <br>

将仅基于词向量的搜索视为你自己系统的起点。<br>

🫠🫠🫠本文档仅介绍基于词向量的搜索，更好的搜索系统不展示，但可以参考以下方案。🚀🚀🚀<br>

Better search systems might combine multiple search methods, along with features like popularity, recency, user history, redundancy with prior search results, click rate data, etc.<br> 

更好的搜索系统可能会结合多种搜索方法，以及诸如流行度、最新性、用户历史记录、与之前搜索结果的重复度、点击率数据等特征。<br>

Q&A retrieval(检索) performance(性能) may also be improved with techniques like [HyDE](https://arxiv.org/abs/2212.10496), in which questions are first transformed into hypothetical(假设的) answers before being embedded. Similarly, GPT can also potentially(潜在的) improve search results by automatically transforming questions into sets of keywords or search terms.<br>

采用HyDE等技术，首先将问题转换成**假设答案**再进行向量化，也可能提升问答检索的性能。同样，GPT也有可能通过自动将问题转换成一组关键词或搜索词，来改善搜索结果。<br>

> HyDE技术可以从 "知识拓展" 获取详细介绍。


## Full procedure(完整流程):

Specifically, this notebook demonstrates the following procedure(具体来说，本notebook演示了以下流程):<br>

1. Prepare search data (once per document)(准备搜索数据（每个文档一次）)

- Collect: We'll download a few hundred Wikipedia articles about the 2022 Olympics(收集：我们将下载几百篇关于2022年奥运会的维基百科文章)
- Chunk: Documents are split into short, mostly self-contained sections to be embedded(分块：将文档分割成短小、基本自含的部分以便向量化)
- Embed: Each section is embedded with the OpenAI API(向量化：每个部分都使用OpenAI API进行向量化)
- Store: Embeddings are saved (for large datasets, use a vector database)(存储：保存词向量结果（对于大型数据集，使用向量数据库）)

2. Search (once per query)(搜索（每次查询一次）)

- Given a user question, generate an embedding for the query from the OpenAI API(根据用户问题，使用OpenAI API生成查询的词向量)
- Using the embeddings, rank the text sections by relevance to the query(利用词向量，根据与查询的相关性对文本部分进行排名)

3. Ask (once per query)(询问（每次查询一次）)

- Insert the question and the most relevant sections into a message to GPT(将问题和最相关的部分插入到给GPT的消息中)
- Return GPT's answer(返回GPT的回答)


## Costs(成本):

Because GPT is more expensive than embeddings search, a system with a decent volume of queries will have its costs dominated(主导；占据) by step 3.<br>

> "`a decent volume of`"并不是一个固定短语，但它经常被一起使用来表达 "足够大的数量"。

因为GPT的成本高于嵌入搜索，所以对于查询量较大的系统来说，其成本将主要由第三步所占据。<br>

- For `gpt-3.5-turbo` using ~1,000 tokens per query, it costs ~$0.002 per query, or ~500 queries per dollar (as of Apr 2023)(对于使用大约1,000个 tokens 每次查询的gpt-3.5-turbo，每次查询的成本约为$0.002，即每美元约500次查询（截至2023年4月）)

- For `gpt-4`, again assuming ~1,000 tokens per query, it costs ~$0.03 per query, or ~30 queries per dollar (as of Apr 2023)(对于gpt-4，同样假设每次查询大约1,000个 token ，每次查询的成本约为$0.03，即每美元约30次查询（截至2023年4月）)

Of course, exact costs will depend on the system specifics and usage patterns.<br>

当然，确切的成本将取决于系统的具体情况和使用模式。<br>


## Preamble(前言):

We'll begin by(我们将从以下几步开始):<br>

- Importing the necessary libraries(导入必要的库)
- Selecting models for embeddings search and question answering(选择用于向量搜索和问题回答的模型)

```python
# imports
import ast  # for converting embeddings saved as strings back to arrays
from openai import OpenAI # for calling the OpenAI API
import pandas as pd  # for storing text and embeddings data
import tiktoken  # for counting tokens
import os # for getting API token from env variable OPENAI_API_KEY
from scipy import spatial  # for calculating vector similarities for search

# models
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "<your OpenAI API key if not set as env var>"))
```

**Troubleshooting: Installing libraries(故障排除：安装库)**<br>

If you need to install any of the libraries above, run `pip install {library_name}` in your terminal.<br>

如果你需要安装上述任何库，请在终端运行 `pip install {library_name}`。<br>

For example, to install the openai library, run:<br>

例如，要安装 openai 库，请运行：<br>

```bash
pip install openai
```

(You can also do this in a notebook cell with `!pip install openai` or `%pip install openai`.)<br>

(你也可以在notebook单元格中使用 `!pip install openai` 或 `%pip install openai` 来执行此操作。)<br>

After installing, restart the notebook kernel so the libraries can be loaded.<br>

安装完成后，重启notebook内核，以便可以加载库。<br>

安装scipy时提示了下列内容，但终究显示成功安装，后续如果出问题再从这里下手找解决方案:<br>

```txt
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
gradio 4.16.0 requires pydantic>=2.0, but you have pydantic 1.10.12 which is incompatible.
Successfully installed numpy-1.26.3 scipy-1.12.0
```

**Troubleshooting: Setting your API key(故障排除：设置你的 API 密钥)**<br>

The OpenAI library will try to read your API key from the `OPENAI_API_KEY` environment variable. If you haven't already, you can set this environment variable by following these [instructions](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety).<br>

OpenAI 库将尝试从 OPENAI_API_KEY 环境变量读取你的 API 密钥。如果你还没有设置，可以按照这些说明来设置此环境变量。<br>

### Motivating example: GPT cannot answer questions about current events

励志的示例：GPT 无法回答有关当前事件的问题<br>

Because the training data for `gpt-3.5-turbo` and `gpt-4` mostly ends in September 2021, the models cannot answer questions about more recent events, such as the 2022 Winter Olympics.<br>

因为 gpt-3.5-turbo 和 gpt-4 的训练数据大多截止到 2021 年 9 月，这些模型无法回答有关更近期事件的问题，例如 2022 年冬季奥运会。<br>

For example, let's try asking 'Which athletes won the gold medal in curling in 2022?':<br>

例如，让我们尝试问一下“2022年哪些运动员赢得了冰壶项目的金牌？”：<br>

```python
# an example question about the 2022 Olympics
query = 'Which athletes won the gold medal in curling at the 2022 Winter Olympics?'

response = client.chat.completions.create(
    messages=[
        {'role': 'system', 'content': 'You answer questions about the 2022 Winter Olympics.'},
        {'role': 'user', 'content': query},
    ],
    model=GPT_MODEL,
    temperature=0,
)

print(response.choices[0].message.content)
```

终端输出:<br>

```txt
As an AI language model, I don't have real-time data. However, I can provide you with general information. The gold medalists in curling at the 2022 Winter Olympics will be determined during the event. The winners will be the team that finishes in first place in the respective men's and women's curling competitions. To find out the specific gold medalists, you can check the official Olympic website or reliable news sources for the most up-to-date information.
```

意思是: 作为一个人工智能语言模型，我没有实时数据。然而，我可以提供一些一般性的信息。2022年冬季奥运会上冰壶项目的金牌得主将在比赛期间决定。获胜者将是在各自的男子和女子冰壶比赛中排名第一的队伍。要了解具体的金牌得主，你可以查看官方奥运会网站或可靠的新闻来源，以获取最新的信息。<br>

In this case, the model has no knowledge of 2022 and is unable to answer the question.<br>

在这种情况下，模型对2022年的情况一无所知，因此无法回答这个问题。<br>

You can give GPT knowledge about a topic by inserting it into an input message<br>

你可以通过将相关内容插入输入消息中，来使GPT了解某个话题。<br>

To help give the model knowledge of curling at the 2022 Winter Olympics, we can copy and paste the top half of a relevant Wikipedia article into our message:<br>

为了帮助模型了解2022年冬季奥运会的冰壶比赛，我们可以复制粘贴相关维基百科文章的上半部分到我们的消息中：<br>

```txt
# text copied and pasted from: https://en.wikipedia.org/wiki/Curling_at_the_2022_Winter_Olympics
# I didn't bother to format or clean the text, but GPT will still understand it
# the entire article is too long for gpt-3.5-turbo, so I only included the top few sections

wikipedia_article_on_curling = """Curling at the 2022 Winter Olympics

Article
Talk
Read
Edit
View history
From Wikipedia, the free encyclopedia
Curling
at the XXIV Olympic Winter Games
Curling pictogram.svg
Curling pictogram
Venue	Beijing National Aquatics Centre
Dates	2–20 February 2022
No. of events	3 (1 men, 1 women, 1 mixed)
Competitors	114 from 14 nations
← 20182026 →
Men's curling
at the XXIV Olympic Winter Games
Medalists
1st place, gold medalist(s)		 Sweden
2nd place, silver medalist(s)		 Great Britain
3rd place, bronze medalist(s)		 Canada
Women's curling
at the XXIV Olympic Winter Games
Medalists
1st place, gold medalist(s)		 Great Britain
2nd place, silver medalist(s)		 Japan
3rd place, bronze medalist(s)		 Sweden
Mixed doubles's curling
at the XXIV Olympic Winter Games
Medalists
1st place, gold medalist(s)		 Italy
2nd place, silver medalist(s)		 Norway
3rd place, bronze medalist(s)		 Sweden
Curling at the
2022 Winter Olympics
Curling pictogram.svg
Qualification
Statistics
Tournament
Men
Women
Mixed doubles
vte
The curling competitions of the 2022 Winter Olympics were held at the Beijing National Aquatics Centre, one of the Olympic Green venues. Curling competitions were scheduled for every day of the games, from February 2 to February 20.[1] This was the eighth time that curling was part of the Olympic program.

In each of the men's, women's, and mixed doubles competitions, 10 nations competed. The mixed doubles competition was expanded for its second appearance in the Olympics.[2] A total of 120 quota spots (60 per sex) were distributed to the sport of curling, an increase of four from the 2018 Winter Olympics.[3] A total of 3 events were contested, one for men, one for women, and one mixed.[4]

Qualification
Main article: Curling at the 2022 Winter Olympics – Qualification
Qualification to the Men's and Women's curling tournaments at the Winter Olympics was determined through two methods (in addition to the host nation). Nations qualified teams by placing in the top six at the 2021 World Curling Championships. Teams could also qualify through Olympic qualification events which were held in 2021. Six nations qualified via World Championship qualification placement, while three nations qualified through qualification events. In men's and women's play, a host will be selected for the Olympic Qualification Event (OQE). They would be joined by the teams which competed at the 2021 World Championships but did not qualify for the Olympics, and two qualifiers from the Pre-Olympic Qualification Event (Pre-OQE). The Pre-OQE was open to all member associations.[5]

For the mixed doubles competition in 2022, the tournament field was expanded from eight competitor nations to ten.[2] The top seven ranked teams at the 2021 World Mixed Doubles Curling Championship qualified, along with two teams from the Olympic Qualification Event (OQE) – Mixed Doubles. This OQE was open to a nominated host and the fifteen nations with the highest qualification points not already qualified to the Olympics. As the host nation, China qualified teams automatically, thus making a total of ten teams per event in the curling tournaments.[6]

Summary
Nations	Men	Women	Mixed doubles	Athletes
 Australia			Yes	2
 Canada	Yes	Yes	Yes	12
 China	Yes	Yes	Yes	12
 Czech Republic			Yes	2
 Denmark	Yes	Yes		10
 Great Britain	Yes	Yes	Yes	10
 Italy	Yes		Yes	6
 Japan		Yes		5
 Norway	Yes		Yes	6
 ROC	Yes	Yes		10
 South Korea		Yes		5
 Sweden	Yes	Yes	Yes	11
 Switzerland	Yes	Yes	Yes	12
 United States	Yes	Yes	Yes	11
Total: 14 NOCs	10	10	10	114
Competition schedule

The Beijing National Aquatics Centre served as the venue of the curling competitions.
Curling competitions started two days before the Opening Ceremony and finished on the last day of the games, meaning the sport was the only one to have had a competition every day of the games. The following was the competition schedule for the curling competitions:

RR	Round robin	SF	Semifinals	B	3rd place play-off	F	Final
Date
Event
Wed 2	Thu 3	Fri 4	Sat 5	Sun 6	Mon 7	Tue 8	Wed 9	Thu 10	Fri 11	Sat 12	Sun 13	Mon 14	Tue 15	Wed 16	Thu 17	Fri 18	Sat 19	Sun 20
Men's tournament								RR	RR	RR	RR	RR	RR	RR	RR	RR	SF	B	F	
Women's tournament									RR	RR	RR	RR	RR	RR	RR	RR	SF	B	F
Mixed doubles	RR	RR	RR	RR	RR	RR	SF	B	F												
Medal summary
Medal table
Rank	Nation	Gold	Silver	Bronze	Total
1	 Great Britain	1	1	0	2
2	 Sweden	1	0	2	3
3	 Italy	1	0	0	1
4	 Japan	0	1	0	1
 Norway	0	1	0	1
6	 Canada	0	0	1	1
Totals (6 entries)	3	3	3	9
Medalists
Event	Gold	Silver	Bronze
Men
details	 Sweden
Niklas Edin
Oskar Eriksson
Rasmus Wranå
Christoffer Sundgren
Daniel Magnusson	 Great Britain
Bruce Mouat
Grant Hardie
Bobby Lammie
Hammy McMillan Jr.
Ross Whyte	 Canada
Brad Gushue
Mark Nichols
Brett Gallant
Geoff Walker
Marc Kennedy
Women
details	 Great Britain
Eve Muirhead
Vicky Wright
Jennifer Dodds
Hailey Duff
Mili Smith	 Japan
Satsuki Fujisawa
Chinami Yoshida
Yumi Suzuki
Yurika Yoshida
Kotomi Ishizaki	 Sweden
Anna Hasselborg
Sara McManus
Agnes Knochenhauer
Sofia Mabergs
Johanna Heldin
Mixed doubles
details	 Italy
Stefania Constantini
Amos Mosaner	 Norway
Kristin Skaslien
Magnus Nedregotten	 Sweden
Almida de Val
Oskar Eriksson
Teams
Men
 Canada	 China	 Denmark	 Great Britain	 Italy
Skip: Brad Gushue
Third: Mark Nichols
Second: Brett Gallant
Lead: Geoff Walker
Alternate: Marc Kennedy

Skip: Ma Xiuyue
Third: Zou Qiang
Second: Wang Zhiyu
Lead: Xu Jingtao
Alternate: Jiang Dongxu

Skip: Mikkel Krause
Third: Mads Nørgård
Second: Henrik Holtermann
Lead: Kasper Wiksten
Alternate: Tobias Thune

Skip: Bruce Mouat
Third: Grant Hardie
Second: Bobby Lammie
Lead: Hammy McMillan Jr.
Alternate: Ross Whyte

Skip: Joël Retornaz
Third: Amos Mosaner
Second: Sebastiano Arman
Lead: Simone Gonin
Alternate: Mattia Giovanella

 Norway	 ROC	 Sweden	 Switzerland	 United States
Skip: Steffen Walstad
Third: Torger Nergård
Second: Markus Høiberg
Lead: Magnus Vågberg
Alternate: Magnus Nedregotten

Skip: Sergey Glukhov
Third: Evgeny Klimov
Second: Dmitry Mironov
Lead: Anton Kalalb
Alternate: Daniil Goriachev

Skip: Niklas Edin
Third: Oskar Eriksson
Second: Rasmus Wranå
Lead: Christoffer Sundgren
Alternate: Daniel Magnusson

Fourth: Benoît Schwarz
Third: Sven Michel
Skip: Peter de Cruz
Lead: Valentin Tanner
Alternate: Pablo Lachat

Skip: John Shuster
Third: Chris Plys
Second: Matt Hamilton
Lead: John Landsteiner
Alternate: Colin Hufman

Women
 Canada	 China	 Denmark	 Great Britain	 Japan
Skip: Jennifer Jones
Third: Kaitlyn Lawes
Second: Jocelyn Peterman
Lead: Dawn McEwen
Alternate: Lisa Weagle

Skip: Han Yu
Third: Wang Rui
Second: Dong Ziqi
Lead: Zhang Lijun
Alternate: Jiang Xindi

Skip: Madeleine Dupont
Third: Mathilde Halse
Second: Denise Dupont
Lead: My Larsen
Alternate: Jasmin Lander

Skip: Eve Muirhead
Third: Vicky Wright
Second: Jennifer Dodds
Lead: Hailey Duff
Alternate: Mili Smith

Skip: Satsuki Fujisawa
Third: Chinami Yoshida
Second: Yumi Suzuki
Lead: Yurika Yoshida
Alternate: Kotomi Ishizaki

 ROC	 South Korea	 Sweden	 Switzerland	 United States
Skip: Alina Kovaleva
Third: Yulia Portunova
Second: Galina Arsenkina
Lead: Ekaterina Kuzmina
Alternate: Maria Komarova

Skip: Kim Eun-jung
Third: Kim Kyeong-ae
Second: Kim Cho-hi
Lead: Kim Seon-yeong
Alternate: Kim Yeong-mi

Skip: Anna Hasselborg
Third: Sara McManus
Second: Agnes Knochenhauer
Lead: Sofia Mabergs
Alternate: Johanna Heldin

Fourth: Alina Pätz
Skip: Silvana Tirinzoni
Second: Esther Neuenschwander
Lead: Melanie Barbezat
Alternate: Carole Howald

Skip: Tabitha Peterson
Third: Nina Roth
Second: Becca Hamilton
Lead: Tara Peterson
Alternate: Aileen Geving

Mixed doubles
 Australia	 Canada	 China	 Czech Republic	 Great Britain
Female: Tahli Gill
Male: Dean Hewitt

Female: Rachel Homan
Male: John Morris

Female: Fan Suyuan
Male: Ling Zhi

Female: Zuzana Paulová
Male: Tomáš Paul

Female: Jennifer Dodds
Male: Bruce Mouat

 Italy	 Norway	 Sweden	 Switzerland	 United States
Female: Stefania Constantini
Male: Amos Mosaner

Female: Kristin Skaslien
Male: Magnus Nedregotten

Female: Almida de Val
Male: Oskar Eriksson

Female: Jenny Perret
Male: Martin Rios

Female: Vicky Persinger
Male: Chris Plys
"""
```

```python
query = f"""Use the below article on the 2022 Winter Olympics to answer the subsequent question. If the answer cannot be found, write "I don't know."

Article:
\"\"\"
{wikipedia_article_on_curling}
\"\"\"

Question: Which athletes won the gold medal in curling at the 2022 Winter Olympics?"""

response = client.chat.completions.create(
    messages=[
        {'role': 'system', 'content': 'You answer questions about the 2022 Winter Olympics.'},
        {'role': 'user', 'content': query},
    ],
    model=GPT_MODEL,
    temperature=0,
)

print(response.choices[0].message.content)
```

此时终端输出:<br>

```txt
In the men's curling event, the gold medal was won by Sweden. In the women's curling event, the gold medal was won by Great Britain. In the mixed doubles curling event, the gold medal was won by Italy.
```

意思是:在男子冰壶比赛中，瑞典赢得了金牌。在女子冰壶比赛中，英国赢得了金牌。在混合双打冰壶比赛中，意大利赢得了金牌。<br>

Thanks to the Wikipedia article included in the input message, GPT answers correctly.<br>

多亏了输入消息中包含的维基百科文章，GPT正确地给出了答案。<br>

In this particular case, GPT was intelligent enough to realize that the original question was underspecified("未明确指定的",读法为 [ʌndərˈspɛsɪfaɪd]), as there were three curling gold medal events, not just one.<br>

在这个特定的情况下，GPT足够聪明地意识到原始问题描述不够具体，因为有三个冰壶金牌赛事，而不仅仅一个。<br>

Of course, this example partly relied on human intelligence. We knew the question was about curling, so we inserted a Wikipedia article on curling.<br>

当然，这个例子部分地依赖于人类智能。我们知道问题是关于冰壶的，所以我们插入了一篇关于冰壶的维基百科文章。<br>

The rest of this notebook shows how to automate(自动化) this knowledge insertion with embeddings-based search.<br>

本notebook的其余部分展示了如何利用基于词向量的搜索自动化这种知识插入。<br>

## 1. Prepare search data(准备搜索数据):

To save you the time & expense, we've prepared a pre-embedded dataset of a few hundred Wikipedia articles about the 2022 Winter Olympics.<br>

为了节省你的时间和费用，我们准备了一个预向量化的数据集，其中包含了几百篇关于2022年冬季奥运会的维基百科文章。<br>

To see how we constructed this dataset, or to modify it yourself, see [Embedding Wikipedia articles for search](https://cookbook.openai.com/examples/embedding_wikipedia_articles_for_search).<br>

要了解我们如何构建这个数据集，或者自行修改它，请参阅嵌入维基百科文章以供搜索。<br>

```python
# download pre-chunked text and pre-computed embeddings
# this file is ~200 MB, so may take a minute depending on your connection speed
embeddings_path = "https://cdn.openai.com/API/examples/data/winter_olympics_2022.csv"

df = pd.read_csv(embeddings_path)
```

```python
# convert embeddings from CSV str type back to list type
df['embedding'] = df['embedding'].apply(ast.literal_eval)
# the dataframe has two columns: "text" and "embedding"
df
```

终端显示:<br>

| #    | text                                          | embedding                                   |
|------|-----------------------------------------------|---------------------------------------------|
| 0    | Lviv bid for the 2022 Winter Olympics\n{...   | [-0.00502106780162955, 0.0026050032465718687, ... |
| 1    | Lviv bid for the 2022 Winter Olympics\n{...   | [0.0033927420154213905, -0.007447326090186834, ... |
| 2    | Lviv bid for the 2022 Winter Olympics\n{...   | [-0.00915789045393467, -0.008366798982024193, ... |
| 3    | Lviv bid for the 2022 Winter Olympics\n{...   | [0.003095189109446182, -0.0060643148680585073, ... |
| 4    | Lviv bid for the 2022 Winter Olympics\n{...   | [-0.002936174161732197, -0.006185177247971296, ... |
| ...  | ...                                           | ...                                           |
| 6054 | Anais Chevalier-Bouchet\n==Personal life==\n...| [-0.027750400826334953, 0.001746018067933619, ... |
| 6055 | Uliana Nigmatullina\n{\n==short description | Rus... | [-0.0217141676694915474, 0.016001321375370026, ... |
| 6056 | Uliana Nigmatullina\n==Biathlon results==\n... | [-0.029143543913960457, 0.014653431840574741, ... |
| 6057 | Uliana Nigmatullina\n==Biathlon results==\n... | [-0.024266039952637565, 0.011665306985378265, ... |
| 6058 | Uliana Nigmatullina\n==Biathlon results==\n... | [-0.021818075329365323, 0.005420385394245386, ... |

6059 rows × 2 columns<br>


2. Search(搜索)

Now we'll define a search function that:<br>

我们来定义一个搜索函数，具体要求如下：<br>

- Takes a user query and a dataframe with text & embedding columns(接收用户查询和一个包含文本和嵌入列的数据框)
- Embeds the user query with the OpenAI API(利用 OpenAI API 对用户查询进行嵌入)
- Uses distance between query embedding and text embeddings to rank the texts(使用查询嵌入和文本嵌入之间的距离对文本进行排序)
- Returns two lists:(返回两个列表)
    - The top N texts, ranked by relevance(按相关性排名的前 N 个文本)
    - Their corresponding relevance scores(它们对应的相关性分数)

```python
# search function
def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response.data[0].embedding
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]
```

`relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y)`是一个Python表达式，定义了一个名为`relatedness_fn`的函数，该函数用于计算两个向量`x`和`y`之间的相似度或相关性。这个函数是在使用`lambda`函数（一个匿名函数）的基础上定义的，并且依赖于`scipy.spatial.distance.cosine`函数来计算**余弦距离**。<br>

## 3. Ask(询问)

With the search function above, we can now automatically retrieve relevant knowledge and insert it into messages to GPT.<br>

通过上述的搜索功能，我们现在可以自动检索相关知识并将其插入到发往GPT的消息中。<br>

Below, we define a function ask that(下面，我们定义了一个名为“查询”的函数，该函数):<br>

- Takes a user query(接收用户的查询请求)
- Searches for text relevant to the query(搜索与查询相关的文本)
- Stuffs(在这里的意思是“填充”或“塞入”) that text into a message for GPT(将该文本填充到发往GPT的消息中)
- Sends the message to GPT(将消息发送给GPT)
- Returns GPT's answer(返回GPT的回答)

```python
def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def query_message(
    query: str,
    df: pd.DataFrame,
    model: str,
    token_budget: int
) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings, relatednesses = strings_ranked_by_relatedness(query, df)
    introduction = 'Use the below articles on the 2022 Winter Olympics to answer the subsequent question. If the answer cannot be found in the articles, write "I could not find an answer."'
    question = f"\n\nQuestion: {query}"
    message = introduction
    for string in strings:
        next_article = f'\n\nWikipedia article section:\n"""\n{string}\n"""'
        if (
            num_tokens(message + next_article + question, model=model)
            > token_budget
        ):
            break
        else:
            message += next_article
    return message + question


def ask(
    query: str,
    df: pd.DataFrame = df,
    model: str = GPT_MODEL,
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message(query, df, model=model, token_budget=token_budget)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": "You answer questions about the 2022 Winter Olympics."},
        {"role": "user", "content": message},
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    response_message = response.choices[0].message.content
    return response_message
```

## Example questions

Finally, let's ask our system our original(最初的) question about gold medal(奖章；获得奖牌) curlers:<br>

最后，让我们用我们最初的问题询问我们的系统关于冬季奥运会冰壶金牌获得者的信息：<br>

```python
# 2022年冬季奥运会冰壶比赛中哪些运动员赢得了金牌？
print(ask('Which athletes won the gold medal in curling at the 2022 Winter Olympics?'))
```

终端显示:<br>

```txt
"In the men's curling tournament, the gold medal was won by the team from Sweden, consisting of Niklas Edin, Oskar Eriksson, Rasmus Wranå, Christoffer Sundgren, and Daniel Magnusson. In the women's curling tournament, the gold medal was won by the team from Great Britain, consisting of Eve Muirhead, Vicky Wright, Jennifer Dodds, Hailey Duff, and Mili Smith."
```

意思是:<br>

```txt
"在男子冰壶比赛中，金牌由瑞典队赢得，队员包括Niklas Edin, Oskar Eriksson, Rasmus Wranå, Christoffer Sundgren, 和 Daniel Magnusson。在女子冰壶比赛中，金牌由英国队赢得，队员包括Eve Muirhead, Vicky Wright, Jennifer Dodds, Hailey Duff, 和 Mili Smith。"
```

Despite `gpt-3.5-turbo` having no knowledge of the 2022 Winter Olympics, our search system was able to retrieve reference text for the model to read, allowing it to correctly list the gold medal winners in the Men's and Women's tournaments.<br>

尽管gpt-3.5-turbo对2022年冬季奥运会没有知识，我们的搜索系统还是能够为模型检索参考文本，使其能够正确列出男子和女子比赛的金牌获得者。<br>

However, it still wasn't quite perfect—the model failed to list the gold medal winners from the Mixed doubles event.<br>

然而，它仍然不够完美——模型未能列出混合双打项目的金牌获得者。<br>


## Troubleshooting wrong answers

To see whether a mistake is from a lack(缺少) of relevant source text (i.e., failure of the search step) or a lack of reasoning reliability (i.e., failure of the ask step), you can look at the text GPT was given by setting `print_message=True`.<br>

要判断一个错误是因为缺乏相关的源文本（即，搜索步骤失败）还是因为缺乏推理的可靠性（即，提问步骤失败），你可以通过设置 `print_message=True` 来查看 GPT 被给予的文本。<br>

In this particular(特定的) case, looking at the text below, it looks like the #1 article given to the model did contain medalists(获奖者) for all three events, but the later results emphasized(强调) the Men's and Women's tournaments(锦标赛；比赛), which may have distracted(使分心) the model from giving a more complete answer.<br>

在这个特定的案例中，查看下面的文本，看起来像是给模型的第一篇文章确实包含了所有三项赛事的奖牌得主，但后续的结果强调了男子和女子比赛，这可能让模型分心，未能给出一个更完整的答案。<br>

```python
# set print_message=True to see the source text GPT was working off of
# 设置 `print_message=True` 查看GPT被给予的文本
print(ask('Which athletes won the gold medal in curling at the 2022 Winter Olympics?', print_message=True))
```

终端显示如下:<br>

```txt
Use the below articles on the 2022 Winter Olympics to answer the subsequent question. If the answer cannot be found in the articles, write "I could not find an answer."

Wikipedia article section:
"""
List of 2022 Winter Olympics medal winners

==Curling==

{{main|Curling at the 2022 Winter Olympics}}
{|{{MedalistTable|type=Event|columns=1|width=225|labelwidth=200}}
|-valign="top"
|Men<br/>{{DetailsLink|Curling at the 2022 Winter Olympics – Men's tournament}}
|{{flagIOC|SWE|2022 Winter}}<br/>[[Niklas Edin]]<br/>[[Oskar Eriksson]]<br/>[[Rasmus Wranå]]<br/>[[Christoffer Sundgren]]<br/>[[Daniel Magnusson (curler)|Daniel Magnusson]]
|{{flagIOC|GBR|2022 Winter}}<br/>[[Bruce Mouat]]<br/>[[Grant Hardie]]<br/>[[Bobby Lammie]]<br/>[[Hammy McMillan Jr.]]<br/>[[Ross Whyte]]
|{{flagIOC|CAN|2022 Winter}}<br/>[[Brad Gushue]]<br/>[[Mark Nichols (curler)|Mark Nichols]]<br/>[[Brett Gallant]]<br/>[[Geoff Walker (curler)|Geoff Walker]]<br/>[[Marc Kennedy]]
|-valign="top"
|Women<br/>{{DetailsLink|Curling at the 2022 Winter Olympics – Women's tournament}}
|{{flagIOC|GBR|2022 Winter}}<br/>[[Eve Muirhead]]<br/>[[Vicky Wright]]<br/>[[Jennifer Dodds]]<br/>[[Hailey Duff]]<br/>[[Mili Smith]]
|{{flagIOC|JPN|2022 Winter}}<br/>[[Satsuki Fujisawa]]<br/>[[Chinami Yoshida]]<br/>[[Yumi Suzuki]]<br/>[[Yurika Yoshida]]<br/>[[Kotomi Ishizaki]]
|{{flagIOC|SWE|2022 Winter}}<br/>[[Anna Hasselborg]]<br/>[[Sara McManus]]<br/>[[Agnes Knochenhauer]]<br/>[[Sofia Mabergs]]<br/>[[Johanna Heldin]]
|-valign="top"
|Mixed doubles<br/>{{DetailsLink|Curling at the 2022 Winter Olympics – Mixed doubles tournament}}
|{{flagIOC|ITA|2022 Winter}}<br/>[[Stefania Constantini]]<br/>[[Amos Mosaner]]
|{{flagIOC|NOR|2022 Winter}}<br/>[[Kristin Skaslien]]<br/>[[Magnus Nedregotten]]
|{{flagIOC|SWE|2022 Winter}}<br/>[[Almida de Val]]<br/>[[Oskar Eriksson]]
|}
"""

Wikipedia article section:
"""
Curling at the 2022 Winter Olympics

==Results summary==

===Women's tournament===

====Playoffs====

=====Gold medal game=====

''Sunday, 20 February, 9:05''
{{#lst:Curling at the 2022 Winter Olympics – Women's tournament|GM}}
{{Player percentages
| team1 = {{flagIOC|JPN|2022 Winter}}
| [[Yurika Yoshida]] | 97%
| [[Yumi Suzuki]] | 82%
| [[Chinami Yoshida]] | 64%
| [[Satsuki Fujisawa]] | 69%
| teampct1 = 78%
| team2 = {{flagIOC|GBR|2022 Winter}}
| [[Hailey Duff]] | 90%
| [[Jennifer Dodds]] | 89%
| [[Vicky Wright]] | 89%
| [[Eve Muirhead]] | 88%
| teampct2 = 89%
}}
"""

Wikipedia article section:
"""
Curling at the 2022 Winter Olympics

==Medal summary==

===Medal table===

{{Medals table
 | caption        = 
 | host           = 
 | flag_template  = flagIOC
 | event          = 2022 Winter
 | team           = 
 | gold_CAN = 0 | silver_CAN = 0 | bronze_CAN = 1
 | gold_ITA = 1 | silver_ITA = 0 | bronze_ITA = 0
 | gold_NOR = 0 | silver_NOR = 1 | bronze_NOR = 0
 | gold_SWE = 1 | silver_SWE = 0 | bronze_SWE = 2
 | gold_GBR = 1 | silver_GBR = 1 | bronze_GBR = 0
 | gold_JPN = 0 | silver_JPN = 1 | bronze_JPN - 0
}}
"""

Wikipedia article section:
"""
Curling at the 2022 Winter Olympics

==Results summary==

===Men's tournament===

====Playoffs====
... ...
```

Knowing that this mistake was due to imperfect(不完美；有缺点的) reasoning in the ask step, rather than imperfect retrieval in the search step, let's focus on improving the ask step.<br>

了解到这个错误是因为提问步骤中的询问，而不是搜索步骤中的检索不完美，我们就专注于改善提问步骤。<br>

The easiest way to improve results is to use a more capable model, such as `GPT-4`. Let's try it.<br>

改善结果的最简单方式是使用更强大的模型，比如 `GPT-4` ，让我们试试看。<br>

```python
# use more powerful model
print(ask('Which athletes won the gold medal in curling at the 2022 Winter Olympics?', model="gpt-4"))
```

终端显示:<br>

```txt
"The athletes who won the gold medal in curling at the 2022 Winter Olympics are:\n\nMen's tournament: Niklas Edin, Oskar Eriksson, Rasmus Wranå, Christoffer Sundgren, and Daniel Magnusson from Sweden.\n\nWomen's tournament: Eve Muirhead, Vicky Wright, Jennifer Dodds, Hailey Duff, and Mili Smith from Great Britain.\n\nMixed doubles tournament: Stefania Constantini and Amos Mosaner from Italy."
```

意思是:<br>

```txt
在2022年冬季奥运会上获得冰壶项目金牌的运动员有：

男子比赛：来自瑞典的Niklas Edin、Oskar Eriksson、Rasmus Wranå、Christoffer Sundgren和Daniel Magnusson。

女子比赛：来自英国的Eve Muirhead、Vicky Wright、Jennifer Dodds、Hailey Duff和Mili Smith。

混合双人比赛：来自意大利的Stefania Constantini和Amos Mosaner。
```

GPT-4 succeeds perfectly, correctly identifying all 12 gold medal winners in curling.<br>

GPT-4 完美成功，准确识别了冰壶项目所有12位金牌获得者。<br>


## More examples(更多)

Below are a few more examples of the system in action. Feel free to try your own questions, and see how it does. <br>

> "Feel free":鼓励某人在没有限制或顾虑的情况下做某事。

以下是一些系统运行中的更多示例。欢迎尝试你自己的问题，看看它的表现如何。<br>

In general, search-based systems do best on questions that have a simple lookup, and worst on questions that require multiple partial sources to be combined and reasoned(合理的；推理) about.<br>

> "reasoned" 为 "reason" 的过去分词和过去式，adj. 合理的;合乎逻辑的;缜密的 v. 推理;理解;思考;推断;推论

通常情况下，基于搜索的系统在需要简单查找的问题上表现最好，而在需要结合和推理多个部分信息源的问题上表现最差。<br>

```python
# counting(计算) question,2022年冬季奥林匹克运动会创造了多少记录？
print(ask('How many records were set at the 2022 Winter Olympics?'))
# 'I could not find an answer.'
```

```python
# comparison(比较) question, 牙买加或古巴在2022年冬季奥运会上的运动员更多吗？
print(ask('Did Jamaica or Cuba have more athletes at the 2022 Winter Olympics?'))

# "Jamaica had more athletes at the 2022 Winter Olympics. According to the provided information, Jamaica had a total of 7 athletes (6 men and 1 woman) competing in 2 sports, while there is no information about Cuba's participation in the 2022 Winter Olympics."

# “在2022年冬季奥运会上，牙买加的运动员更多。根据提供的信息，牙买加共有7名运动员（6男1女）参加了2项运动，而关于古巴参加2022年冬季奥运会的信息则没有。”
```

```python
# subjective question(主观问题),哪项奥林匹克运动最有娱乐性(最有趣)？, entertaining adj. 娱乐的；有趣的
print(ask('Which Olympic sport is the most entertaining?'))
# 'I could not find an answer.'
```


## 知识拓展

### 在NLP领域，什么因素决定了模型的输入长度？

在自然语言处理（NLP）领域，模型的输入长度受到多种因素的影响，主要包括以下几点：<br>

1. **模型架构**：不同的NLP模型架构对输入长度有不同的限制。例如，传统的RNN（循环神经网络）在处理长序列时会遇到梯度消失或梯度爆炸的问题，从而限制了它们处理长输入序列的能力。而基于Transformer的模型，如BERT或GPT系列，虽然能够处理相对更长的序列，但它们仍然有固定的最大输入长度限制，这主要由模型的位置编码和内存限制决定。

2. **位置编码**：Transformer模型通过位置编码来捕获序列中单词的顺序信息。在许多模型实现中，位置编码的长度是预先定义的，这直接限制了模型能够处理的最大序列长度。

3. **内存和计算资源**：处理长序列需要大量的内存和计算资源。模型输入长度的增加会导致计算复杂度和内存需求成倍增长，特别是对于基于Transformer的模型，其自注意力机制的计算复杂度和内存需求是输入长度的平方级别。因此，硬件资源的限制也是决定模型输入长度的一个重要因素。

4. **任务需求和数据特性**：不同的NLP任务和数据集特性也会影响模型输入长度的选择。例如，一些任务可能需要分析长文本（如文档分类或问答系统中的文本理解），而其他任务（如情感分析）可能只需要较短的文本片段。此外，数据的语言和结构也会影响到合适的输入长度。

5. **效率和性能平衡**：虽然较长的输入可以提供更多的上下文信息，有助于模型更好地理解文本，但这也可能导致计算效率降低和训练难度增加。因此，在实际应用中，需要在模型性能和计算效率之间找到一个平衡点，这通常通过实验来确定最优的输入长度。

总的来说，模型的输入长度是由模型架构、技术限制、任务需求和效率考虑等多个因素共同决定的。在设计或选择NLP模型时，需要根据具体任务的需求和可用资源来合理设置输入长度。<br>

### 为什么chatgpt可以用几千甚至几万长度的输入:

ChatGPT，基于OpenAI的GPT（Generative Pre-trained Transformer）模型，能够处理几千甚至几万长度的输入，这得益于几个关键技术和设计选择：<br>

1. **稀疏注意力机制**：虽然标准的Transformer模型使用的全自注意力机制限制了它处理长序列的能力（由于内存和计算成本随序列长度平方增长），但通过采用稀疏注意力机制，GPT能够有效地减少计算复杂度和内存使用。稀疏注意力通过仅在序列的子集上执行注意力计算来实现，从而允许模型处理更长的文本序列。

2. **分块处理**：为了处理长文本，ChatGPT可以将输入文本分割成较小的块或片段，这些块可以独立地被模型处理。然后，模型可以通过某种形式的状态管理或上下文融合技术来整合这些块的输出，以生成连贯的回复。这种方法允许模型间接地处理超出其最大输入长度限制的文本。

3. **内存和上下文缓存机制**：某些Transformer模型的变体，如GPT-3及其后续版本，采用了改进的内存管理和上下文缓存机制，使模型能够在处理连续对话或长文本时“记住”先前的上下文。这意味着模型可以在不同时间点访问和参考之前的输入，即使这些输入在一个操作步骤中超过了模型的标准输入限制。

4. **模型和框架优化**：通过软件和硬件优化，如更高效的矩阵乘法操作、更好的内存管理策略和使用专门的硬件（如GPU或TPU），可以进一步提高模型处理长序列的能力。这些优化有助于降低处理长输入时的延迟和资源需求。

5. **动态注意力窗口和层次化注意力**：一些研究提出了动态调整注意力窗口大小的方法，或者通过层次化的注意力结构来有效处理长距离依赖，这些技术可以进一步提升模型处理长序列的能力。

这些技术和设计策略的组合使得ChatGPT能够有效处理长输入序列，即使是几千到几万个字符的长度，从而在多轮对话、长文本理解和生成等任务中表现出色。然而，值得注意的是，处理非常长的输入仍然会受到实际计算资源和效率的限制。<br>

### HyDE技术是什么？

标准化解释:<br>

HyDE（Hypothetical Document Embeddings）技术是一种信息检索方法，特别用于零样本（Zero-Shot）密集检索场景，不需要相关性标签。这项技术通过生成“假设性文档”来避开传统密集检索中需要的相关性标签。在HyDE中，使用指令跟随型语言模型（如InstructGPT）根据查询生成假设性文档，然后将这个文档编码到一个文档仅嵌入空间中，该空间通过无监督对比学习得到，能够捕获文档之间的相似性。这种方法允许系统在没有任何查询集、文档集或任何相关性评判的情况下，学习查询和文档的嵌入函数，从而实现零样本密集检索。<br>

HyDE的创新之处在于它的能力，可以在没有细粒度调整或相关性标签的情况下，通过生成假设性文档来提高检索的准确率和相关性。这种策略被认为比简单的零样本检索更有效，尽管它生成的文档可能并不事实正确，但能够捕获查询所需的相关性结构。这种方法既避开了直接学习查询和文档编码器的问题，也将问题保持在文档到文档的检索领域内，这是一种已知的无监督技术。<br>

简而言之，HyDE技术通过生成与查询相关但可能不完全准确的假设性文档，然后利用这些文档的嵌入来进行信息检索，有效地解决了零样本密集检索的挑战。<br>

**🐳🐳🐳上面的答案太过于学术，笔者以一种更易于理解的方式解释一下:**<br>

假设你想知道奥运会有哪些比赛项目，如果直接从所有文档中查找，检索的成本过高，且由于问句信息量的限制，检索出的结果可能不够准确。<br>

此时，如果采用让模型先生成一个假设性的答案，然后用这个假设性的答案去和所有真实文档匹配，这样找出的最相似的文档可信度更高，达到的答案也更准确。<br>

简而言之，HyDE技术通过创造一个中间步骤——生成一个假设的答案文档，来帮助找到你真正需要的信息，即使在很复杂的情况下也能工作得很好。这样，即使你提出的问题很难直接找到答案，HyDE技术也能帮你找到相关的信息。<br>

