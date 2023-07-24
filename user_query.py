"""
命令行方式的用户提问搜索
"""
import openai
import os
from embedding import create_embedding
from vector_db import Storage
import json

def limit_context_length(context, max_length=3000):
    """
    限制文本列表的总长度不超过指定的最大值。
    :param context: 文本列表。
    :param max_length: 最大长度限制，默认为3000。
    :return: 截取到的前n个文本段落。
    """
    # 获取每个文本段落的长度。
    paragraph_lengths = [len(paragraph) for paragraph in context]

    total_length = sum(paragraph_lengths)
    if total_length <= max_length:
        # 如果总长度小于等于最大长度限制，则不需要截断文本。
        return context

    # 如果总长度超过最大长度限制，则截取到前n个文本段落。
    current_length = 0
    for index, length in enumerate(paragraph_lengths):
        current_length += length
        if current_length > max_length:
            # 切片复制新的列表，并返回截取到的前n个文本段落。
            return context[:index]

    # 如果所有的文本段落都被包含，则返回整个文本列表。
    return context


def completion(query: str, context: list[str]) -> str:
    """
    根据query和context调用openai ChatCompletion
    """
    context = limit_context_length(context, 3000)

    text = "\n".join(f"{index}. {text.strip()}" for index,
                     text in enumerate(context))
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {'role': 'system',
             'content':  '''
             请根据用户所提供的上下文中进行回复。当无法在User所提供的上下文中查找到相关内容时候，请输出没有相关内容。
             输出格式请以json的格式输出，json的key是content和url , content 回复的内容，url代表所参考的链接列表，非json格式内容不需要输出
             当无法从上下文找到相关内容时
             {
                "content": "没有相关内容",
                "url": []
             }
             
             当可以从上下文找到相关内容时，需要根据相关内容输出回复内容
             {
                "content": "根据上下文回复的内容",
                "url": ["参考的链接"]
             }
             '''},
            {'role': 'user', 'content': f'context：\n{text}\nquestion：{query}'},
        ],
    )
    print(f"使用的tokens: {response.usage.total_tokens}")
    return response.choices[0].message.content


def user_query_loop() -> None:
    """
    Loop for user queries.
    """
    storage = Storage()
    limit = 5
    while True:
        query = input("请输入问题: \n> ")
        if query == "quit":
            break
        _, embedding = create_embedding(query)
        rets = storage.get_texts(embedding, limit)
        # rets = list(set(rets)) # drop duplicated texts
        # print(f"已找到相关片段: {len(rets)}")

        texts = [f'{index}: ' + json.dumps({
            "url": ret[2],
            "content": ret[0]
        }, ensure_ascii=False) + '\n' for index, ret in enumerate(rets)]
        print(texts)
        answer = completion(query, texts)
        print(">> Answer:")
        print(answer.strip())
        print("=====================================")


if __name__ == '__main__':
    user_query_loop()
