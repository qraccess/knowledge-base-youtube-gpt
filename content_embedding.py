"""
遍历Markdown文件，将文件内容分割为合适的大小，并通过embedding将数据存入向量数据库
"""

import os
from typing import Generator
from embedding import create_embedding
from vector_db import Storage
from scrapy import download_youtube_audios
import hashlib


def walk_mds(top: str) -> Generator[str, None, None]:
    """
    该函数用于递归遍历以'top'为根目录的文件夹树，并生成发现的.md文件的文件路径。
    参数:
        top: 开始递归搜索的根目录。
    生成:
        每个发现的.md文件的文件路径。
    """
    for root, dirs, files in os.walk(top, topdown=True):
        for name in files:
            file_path = os.path.join(root, name)
            if file_path.endswith('.md'):
                yield file_path


def split_string(input_string: str) -> Generator[str, None, None]:
    """
    将一个较长的字符串分成最大长度为600的块。
    参数：
        input_string: 要分割的字符串。
    生成：
        输入字符串的每个块, 最大长度为600。overlay = 120
    """
    max_length = 600
    overlay_length = 120
    while len(input_string) > max_length:
        yield input_string[:max_length]
        input_string = input_string[max_length-overlay_length:]
    yield input_string


def md_files_to_string(dir_path: str) -> Generator[Generator[str, None, None], None, None]:
    """
    此函数用于读取给定目录下所有的 .md 文件，并将其内容分成最大长度为 600 的字符串，逐一生成这些字符串。
    参数：
        dir_path: 包含 .md 文件的目录路径。
    生成器输出：
        每个 .md 文件的内容被拆分为长度最大为 600 的多个字符串，逐一生成这些字符串。
    """
    for file_path in walk_mds(dir_path):
        with open(file_path, encoding="utf-8") as f:
            read_data = f.read()
            yield split_string(read_data)


def md_file_to_string(file_path: str) -> Generator[Generator[str, None, None], None, None]:
    """
    此函数用于指定md 文件将其内容分成最大长度为 600 的字符串，重复120字符串，逐一生成这些字符串。
    参数：
        dir_path: 包含 .md 文件的目录路径。
    生成器输出：
        每个 .md 文件的内容被拆分为长度最大为 600 的多个字符串，逐一生成这些字符串。
    """
    with open(file_path, encoding="utf-8") as f:
        read_data = f.read()
        yield split_string(read_data)


def content_to_db(docs_dir: str) -> None:
    """
    将指定目录中的md文件内容添加到数据库中。
    :param docs_dir: md文件所在目录
    """
    storage = Storage()
    for str_list in md_files_to_string(docs_dir):
        for text in str_list:
            try:
                _, vector = create_embedding(str(text))
            except Exception as exce:
                print(str(exce))
                input("wait for command to retry")
                _, vector = create_embedding(str(text))
            storage.add(text, vector, )
            print(f"> 完成插入text: [{text[0:10]}], embedding: {vector[0:3]}")


def get_md5_of_file(file_path: str) -> str:
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def audio_to_db(item) -> None:
    storage = Storage()
    if not os.path.exists(item['md_file']):
        print(f"文件不存在: {item['md_file']}")
        return
    audio_md5 = get_md5_of_file(item['md_file'])
    search_ret = storage.search_identifier(item['identifier'])
    if search_ret is not None:
        if search_ret['md5'] == audio_md5:
            print(f"已存在: {item['identifier']}")
            return
        else:
            storage.delete_identifier(item['identifier'])
    for str_list in md_file_to_string(item['md_file']):
        for text in str_list:
            try:
                _, vector = create_embedding(str(text))
            except Exception as exce:
                print(str(exce))
                input("wait for command to retry")
                _, vector = create_embedding(str(text))

            try:
                storage.add_identifier(item['identifier'], audio_md5)
                storage.add_embedding(text, vector, item['url'], item['title'], item['author'], item['identifier'], item['channel'])
                print(f"> 完成插入text: [{text[0:10]}], embedding: {vector[0:3]}")
            except Exception as e:
                storage.delete_identifier(item['identifier'])
                print(f"插入失败: {e}")


if __name__ == '__main__':

    audios = download_youtube_audios(
        'https://www.youtube.com/watch?v=SfaHCX0qTlQ&list=PLlHw500PGQdJJ_-ENpCy7vVfewvraQCOj')
    for item in audios:
        audio_to_db(item)

    # audio = {
    #     'identifier': 'ftoZfnVVgIw',
    #     'md_file': '/Volumes/KINGSTON/projects/knowledge-base-youtube-gpt/output/md/ftoZfnVVgIw.md',
    #     'url': 'https://www.youtube.com/watch?v=ftoZfnVVgIw'
    # }
    # audio_to_db(audio)
