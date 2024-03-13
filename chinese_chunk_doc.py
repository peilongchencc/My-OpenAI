import os
import re
import pickle
import hashlib
from typing import List, Optional, Any  # 导入类型注解工具，用于函数和变量的类型定义。
import pandas as pd
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger
from tqdm import tqdm
from contextlib import contextmanager

pwd_path = os.path.abspath(os.path.dirname(__file__))

local_embedding = False # 是否使用本地embedding

@contextmanager
def retrieve_proxy(proxy=None):
    """
    1, 如果proxy = NONE，设置环境变量，并返回最新设置的代理
    2，如果proxy ！= NONE，更新当前的代理配置，但是不更新环境变量
    """
    global http_proxy, https_proxy
    if proxy is not None:
        http_proxy = proxy
        https_proxy = proxy
        yield http_proxy, https_proxy
    else:
        old_var = os.environ["HTTP_PROXY"], os.environ["HTTPS_PROXY"]
        os.environ["HTTP_PROXY"] = http_proxy
        os.environ["HTTPS_PROXY"] = https_proxy
        yield http_proxy, https_proxy  # return new proxy

        # return old proxy
        os.environ["HTTP_PROXY"], os.environ["HTTPS_PROXY"] = old_var

chunk_overlap = 50
chunk_size = 500
hf_emb_model_name = "shibing624/text2vec-base-multilingual"

OPENAI_API_BASE = "https://api.openai.com/v1"

def sheet_to_string(sheet, sheet_name=None):
    result = []
    for index, row in sheet.iterrows():
        row_string = ""
        for column in sheet.columns:
            row_string += f"{column}: {row[column]}, "
        row_string = row_string.rstrip(", ")
        row_string += "."
        result.append(row_string)
    return result

def excel_to_string(file_path):
    # 读取Excel文件中的所有工作表
    excel_file = pd.read_excel(file_path, engine="openpyxl", sheet_name=None)

    # 初始化结果字符串
    result = []

    # 遍历每一个工作表
    for sheet_name, sheet_data in excel_file.items():
        # 处理当前工作表并添加到结果字符串
        result += sheet_to_string(sheet_data, sheet_name=sheet_name)

    return result

def get_files_hash(file_src=None, file_paths=None):
    if file_src:
        file_paths = [x.name for x in file_src]
    file_paths.sort(key=lambda x: os.path.basename(x))

    md5_hash = hashlib.md5()
    for file_path in file_paths:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                md5_hash.update(chunk)

    return md5_hash.hexdigest()

def load_pkl(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data

def save_pkl(data, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)

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


def get_documents(file_paths):
    text_splitter = ChineseRecursiveTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    documents = []
    logger.debug("Loading documents...")
    logger.debug(f"file_paths: {file_paths}")
    for file in file_paths:
        filepath = file.name
        filename = os.path.basename(filepath)
        file_type = os.path.splitext(filename)[1]
        logger.info(f"loading file: {filename}")
        texts = None
        try:
            if file_type == ".docx":
                logger.debug("Loading Word...")
                from langchain.document_loaders import UnstructuredWordDocumentLoader
                loader = UnstructuredWordDocumentLoader(filepath)
                texts = loader.load()
            elif file_type == ".pptx":
                logger.debug("Loading PowerPoint...")
                from langchain.document_loaders import UnstructuredPowerPointLoader
                loader = UnstructuredPowerPointLoader(filepath)
                texts = loader.load()
            elif file_type == ".epub":
                logger.debug("Loading EPUB...")
                from langchain.document_loaders import UnstructuredEPubLoader
                loader = UnstructuredEPubLoader(filepath)
                texts = loader.load()
            elif file_type == ".xlsx":
                logger.debug("Loading Excel...")
                text_list = excel_to_string(filepath)
                texts = []
                for elem in text_list:
                    texts.append(Document(page_content=elem,
                                          metadata={"source": filepath}))
            else:
                logger.debug("Loading text file...")
                from langchain.document_loaders import TextLoader
                loader = TextLoader(filepath, "utf8")
                texts = loader.load()
            logger.debug(f"text size: {len(texts)}, text top3: {texts[:3]}")
        except Exception as e:
            logger.error(f"Error loading file: {filename}, {e}")

        if texts is not None:
            texts = text_splitter.split_documents(texts)
            documents.extend(texts)
    logger.debug(f"Documents loaded. documents size: {len(documents)}, top3: {documents[:3]}")
    return documents


def construct_index(
        api_key,
        files,
        load_from_cache_if_possible=True,
):
    from langchain.vectorstores import FAISS
    from langchain.embeddings.huggingface import HuggingFaceEmbeddings
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    else:
        os.environ["OPENAI_API_KEY"] = "sk-xxxxxxx"
    index_name = get_files_hash(files)
    index_dir = os.path.join(pwd_path, '../index')
    index_path = f"{index_dir}/{index_name}"
    doc_file = f"{index_path}/docs.pkl"
    if local_embedding:
        embeddings = HuggingFaceEmbeddings(model_name=hf_emb_model_name)
    else:
        from langchain.embeddings import OpenAIEmbeddings
        if os.environ.get("OPENAI_API_TYPE", "openai") == "openai":
            openai_api_base = os.environ.get("OPENAI_API_BASE", OPENAI_API_BASE)
            embeddings = OpenAIEmbeddings(
                openai_api_base=openai_api_base,
                openai_api_key=os.environ.get("OPENAI_EMBEDDING_API_KEY", api_key)
            )
        else:
            embeddings = OpenAIEmbeddings(
                deployment=os.environ["AZURE_EMBEDDING_DEPLOYMENT_NAME"],
                openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
                model=os.environ["AZURE_EMBEDDING_MODEL_NAME"],
                openai_api_base=os.environ["AZURE_OPENAI_API_BASE_URL"],
                openai_api_type="azure"
            )
    if os.path.exists(index_path) and load_from_cache_if_possible:
        logger.info("找到了缓存的索引文件，加载中……")
        index = FAISS.load_local(index_path, embeddings)
        documents = load_pkl(doc_file)
        return index, documents
    else:
        try:
            documents = get_documents(files)
            logger.info("构建索引中……")
            with retrieve_proxy():
                index = FAISS.from_documents(documents, embeddings)
            logger.debug("索引构建完成！")
            os.makedirs(index_dir, exist_ok=True)
            index.save_local(index_path)
            logger.debug("索引已保存至本地!")
            save_pkl(documents, doc_file)
            logger.debug("索引文档已保存至本地!")
            return index, documents
        except Exception as e:
            logger.error(f"索引构建失败！error: {e}")
            return None
