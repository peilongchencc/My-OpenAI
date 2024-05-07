# Similarity Search with Milvus and OpenAI:

使用 Milvus 和 OpenAI 进行相似性搜索<br>

This page discusses vector database integration with OpenAI's embedding API.<br>

本页面讨论了向量数据库与 OpenAI embedding API 的集成。<br>

We'll showcase how [OpenAI's Embedding API](https://platform.openai.com/docs/guides/embeddings) can be used with our vector database to search across book titles.<br>

我们将展示如何利用 OpenAI 的 Embedding API 与我们的向量数据库一起搜索书籍标题。<br>

Many existing book search solutions (such as those used by public libraries, for example) rely on keyword matching rather than a semantic understanding of what the title is actually about.<br>

许多现有的书籍搜索解决方案（例如公共图书馆使用的那些）依赖于 **关键词匹配** 🚨，而不是对标题实际含义的语义理解。<br>

Using a trained model to represent the input data is known as semantic search, and can be expanded to a variety of different text-based use cases, including anomaly detection and document search.<br>

使用训练好的模型来表示输入数据被称为 **语义搜索** ✅，可以扩展到各种不同的基于文本的用例，包括异常检测和文档搜索。<br>


## Getting started:

The only prerequisite you'll need here is an API key from the OpenAI website.<br>

这里唯一需要的前提是从 OpenAI 网站获取一个 API 密钥。<br>

Be sure you have already started up a Milvus instance.<br>

请确保您已经启动了 Milvus 实例。<br>

We'll also prepare the data that we're going to use for this example. You can grab the book titles [here](https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks?resource=download).<br>

我们还会准备好这个例子中要使用的数据，您可以在这里获取书名。<br>

Let's create a function to load book titles from our CSV. <br>

我们来创建一个函数，从我们的 CSV 文件加载书名。<br>

```python
import csv
import json
import random
import time
from openai import OpenAI
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
```

```python
def csv_load(file):
    with open(file, newline='') as f:
        reader=csv.reader(f, delimiter=',')
        for row in reader:
            yield row[1]
```

With this, we're ready to move on to generating embeddings. <br>

有了这个，我们已经准备好开始生成嵌入向量了。<br>


## Searching book titles with OpenAI & Milvus(使用OpenAI和Milvus搜索书名):

Here we can find the main parameters that need to be modified for running with your own accounts.<br>

在这里，我们可以找到需要修改以适应您自己帐户的主要参数。<br>

Beside each is a description of what it is.<br>

每个参数旁边都有其描述。<br>

```python
FILE = './content/books.csv'  # Download it from https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks and save it in the folder that holds your script.
COLLECTION_NAME = 'title_db'  # Collection name
DIMENSION = 1536  # Embeddings size
COUNT = 100  # How many titles to embed and insert.
MILVUS_HOST = 'localhost'  # Milvus server URI
MILVUS_PORT = '19530'
OPENAI_ENGINE = 'text-embedding-3-small'  # Which engine to use, you can change it into `text-embedding-3-large` or `text-embedding-ada-002`
client = OpenAI()
client.api_key = 'sk-******'  # Use your own Open AI API Key here
```

```log
Note(注意):

Because the embedding process for a free OpenAI account is relatively time-consuming, we use a set of data small enough to reach a balance between the script executing time and the precision of the search results.

由于免费OpenAI帐户的嵌入过程相对耗时，我们使用了足够小的数据集来在脚本执行时间和搜索结果精度之间达到平衡。

You can change the COUNT constant to fit your needs.

您可以更改COUNT常量以满足您的需求。
```

This segment deals with Milvus and setting up the database for this use case.<br>

这一部分涉及Milvus以及为此用例设置数据库。<br>

Within Milvus, we need to set up a collection and index the collection.<br>

在Milvus中，我们需要设置一个集合并对该集合进行索引。<br>

For more information on how to use Milvus, look [here](https://milvus.io/docs/quickstart.md).<br>

想要了解更多关于如何使用Milvus的信息，请看这里。<br>

```python
connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

if utility.has_collection(COLLECTION_NAME):
    utility.drop_collection(COLLECTION_NAME)

fields = [
    FieldSchema(name='id', dtype=DataType.INT64, descrition='Ids', is_primary=True, auto_id=False),
    FieldSchema(name='title', dtype=DataType.VARCHAR, description='Title texts', max_length=200),
    FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, description='Embedding vectors', dim=DIMENSION)
]
schema = CollectionSchema(fields=fields, description='Title collection')
collection = Collection(name=COLLECTION_NAME, schema=schema)

index_params = {
    'index_type': 'IVF_FLAT',
    'metric_type': 'L2',
    'params': {'nlist': 1024}
}
collection.create_index(field_name="embedding", index_params=index_params)
```

Once we have the collection setup we need to start inserting our data.<br>

一旦我们设置好了集合，我们就需要开始插入我们的数据。<br>

This is in three steps: reading the data, embedding the titles, and inserting into Milvus.<br>

这可以分为三个步骤：读取数据，对标题进行嵌入，然后插入到Milvus中。<br>

```python
def embed(text):
    response = client.embeddings.create(
        input=text,
        model=OPENAI_ENGINE
    )
    return response.data[0].embedding

for idx, text in enumerate(random.sample(sorted(csv_load(FILE)), k=COUNT)):  # Load COUNT amount of random values from dataset
    ins=[[idx], [(text[:198] + '..') if len(text) > 200 else text], [embed(text)]]  # Insert the title id, the title text, and the title embedding vector
    collection.insert(ins)
    time.sleep(3)  # Free OpenAI account limited to 60 RPM
```

```python
collection.load()

def search(text):
    # Search parameters for the index
    search_params={
        "metric_type": "L2"
    }

    results=collection.search(
        data=[embed(text)],  # Embeded search value
        anns_field="embedding",  # Search across embeddings
        param=search_params,
        limit=5,  # Limit to five results per search
        output_fields=['title']  # Include title field in result
    )

    ret=[]
    for hit in results[0]:
        row=[]
        row.extend([hit.id, hit.score, hit.entity.get('title')])  # Get the id, distance, and title for the results
        ret.append(row)
    return ret

search_terms=['self-improvement', 'landscape']

for x in search_terms:
    print('Search term:', x)
    for result in search(x):
        print(result)
    print()
```

You should see the following as the output:<br>

您应该会看到以下内容作为输出：<br>

```log
Search term: self-improvement
[46, 0.37948882579803467, 'The Road Less Traveled: A New Psychology of Love  Traditional Values  and Spiritual Growth']
[24, 0.39301538467407227, 'The Leader In You: How to Win Friends  Influence People and Succeed in a Changing World']
[35, 0.4081816077232361, 'Think and Grow Rich: The Landmark Bestseller Now Revised and Updated for the 21st Century']
[93, 0.4174671173095703, 'Great Expectations']
[10, 0.41889268159866333, 'Nicomachean Ethics']

Search term: landscape
[49, 0.3966977894306183, 'Traveller']
[20, 0.41044068336486816, 'A Parchment of Leaves']
[40, 0.4179283380508423, 'The Illustrated Garden Book: A New Anthology']
[97, 0.42227691411972046, 'Monsoon Summer']
[70, 0.42461898922920227, 'Frankenstein']
```