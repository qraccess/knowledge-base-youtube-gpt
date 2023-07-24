"""
利用openai的embedding api生成词向量
"""
import openai
from dotenv import load_dotenv

import os

load_dotenv()
openai.api_key = os.getenv("API_KEY")


def create_embedding(text: str):
    """Create an embedding for the provided text."""
    embedding = openai.Embedding.create(
        model="text-embedding-ada-002", input=text)
    return text, embedding.data[0].embedding
