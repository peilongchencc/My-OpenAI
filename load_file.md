## LangChain加载TXT文件的方式:

```python
from langchain_community.document_loaders import TextLoader

# 替换为你的文本文件的路径
filepath = 'example_data.txt'

loader = TextLoader(filepath)

# 使用加载器加载文档
document = loader.load()

# 打印加载的文档内容
print(document) # list
# 具体的文章内容
print(document[0].page_content) # string
```