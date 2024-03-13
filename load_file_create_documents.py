import os
import re
import pickle
import hashlib
from typing import List, Optional, Any  # 导入类型注解工具，用于函数和变量的类型定义。
import pandas as pd
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter  # RecursiveCharacterTextSplitter 的父类为 TextSplitter，后续调用的 split_documents 其实是 TextSplitter 的方法。
from loguru import logger
from tqdm import tqdm
from contextlib import contextmanager
from langchain_community.document_loaders import TextLoader


class ChineseRecursiveTextSplitter(RecursiveCharacterTextSplitter):
    """Recursive text splitter for Chinese text.
    copy from: https://github.com/chatchat-space/Langchain-Chatchat/tree/master
    递归文本分割器，专门用于处理中文文本。
    代码来源：https://github.com/chatchat-space/Langchain-Chatchat/tree/master
    """

    def __init__(
            self,
            separators: Optional[List[str]] = None, # 分隔符列表，用于分割文本。
            keep_separator: bool = True,            # 是否保留分隔符。
            is_separator_regex: bool = True,        # 分隔符是否为正则表达式。
            **kwargs: Any,
    ) -> None:
        """Create a new TextSplitter.创建一个新的TextSplitter实例。"""
        super().__init__(keep_separator=keep_separator, **kwargs)   # 调用基类的构造函数。
        self._separators = separators or [
            "\n\n",  # 段落分隔符。
            "\n",  # 行分隔符。
            "。|！|？",  # 句号、感叹号、问号。
            "\.\s|\!\s|\?\s",  # 英文句号、感叹号、问号后跟空格。
            "；|;\s",  # 中文分号、英文分号后跟空格。
            "，|,\s"  # 中文逗号、英文逗号后跟空格。
        ]
        self._is_separator_regex = is_separator_regex  # 设置是否将分隔符视为正则表达式的标志。

    @staticmethod
    def _split_text_with_regex_from_end(
            text: str, separator: str, keep_separator: bool
    ) -> List[str]:
        # Now that we have the separator, split the text
        """使用正则表达式从文本末尾开始分割文本。"""
        # 使用指定的分隔符分割文本。
        if separator:
            if keep_separator:
                # 在模式中使用括号来保留结果中的分隔符。
                # The parentheses in the pattern keep the delimiters in the result.
                _splits = re.split(f"({separator})", text)
                splits = ["".join(i) for i in zip(_splits[0::2], _splits[1::2])]
                if len(_splits) % 2 == 1:
                    splits += _splits[-1:]
            else:
                splits = re.split(separator, text)
        else:
            splits = list(text)
        return [s for s in splits if s != ""]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Split incoming text and return chunks.分割传入的文本并返回文本块。"""
        final_chunks = []   # 最终的文本块列表
        # Get appropriate separator to use
        # 确定使用哪个分隔符。
        separator = separators[-1]
        new_separators = []
        for i, _s in enumerate(separators):
            _separator = _s if self._is_separator_regex else re.escape(_s)
            if _s == "":
                separator = _s
                break
            if re.search(_separator, text):
                separator = _s
                new_separators = separators[i + 1:]
                break

        _separator = separator if self._is_separator_regex else re.escape(separator)
        splits = self._split_text_with_regex_from_end(text, _separator, self._keep_separator)

        # Now go merging things, recursively splitting longer texts.
        # 递归分割较长的文本。
        _good_splits = []
        _separator = "" if self._keep_separator else separator
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(_good_splits, _separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    # 如果当前文本块过长且还有其他分隔符可用，则递归使用其他分隔符进行分割。
                    other_info = self._split_text(s, new_separators)
                    final_chunks.extend(other_info)
        if _good_splits:
            # 如果还有未处理的好的分割块，合并它们并添加到最终的文本块列表中。
            merged_text = self._merge_splits(_good_splits, _separator)
            final_chunks.extend(merged_text)
        # 对最终的文本块进行清理，移除多余的换行符，并确保文本块非空。
        return [re.sub(r"\n{2,}", "\n", chunk.strip()) for chunk in final_chunks if chunk.strip() != ""]

chunk_overlap = 50
chunk_size = 500

def get_documents(filepath):
    text_splitter = ChineseRecursiveTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    # 使用LangChain内置txt文件加载器
    loader = TextLoader(filepath)
    # 使用加载器加载文档
    texts = loader.load()   # 数据类型为list [Document(page_content='（一）直接打压式\n洗盘\n直接打压较多出现在 庄家 吸货区域，目的是... metadata={'source': 'example_data.txt'}' metadata={'source': 'example_data.txt'})]
    documents = []
    if texts is not None:
        all_content = texts[0].page_content
        texts = text_splitter.create_documents([all_content])   # 注意要将string转为list
        documents.extend(texts)
    return documents

if __name__ == "__main__":
    # 替换为你的文本文件的路径
    filepath = 'example_data.txt'
    # 获取分割后的所有内容，最终数据类型为list
    splited_content = get_documents(filepath)
    # print(splited_content)
    print(len(splited_content))
    for each_content in splited_content:
        print(each_content)