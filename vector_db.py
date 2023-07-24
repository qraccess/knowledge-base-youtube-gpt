"""
PostgreSQL + pgvector实现向量数据库
"""
from pgvector.sqlalchemy import Vector
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Sequence
from typing import Optional

Base = declarative_base()
SQL_URL = "postgresql://postgres:postgres@localhost:5432/chatbot"


class EmbeddingEntity(Base):
    __tablename__ = 'knowledge'
    id = Column(Integer, Sequence('embedding_entity_id_seq'), primary_key=True)
    detail = Column(String)
    embedding = Column(Vector(1536))
    url = Column(String(256))
    title = Column(String(256))
    author = Column(String(32))
    identifier = Column(String(256))
    channel = Column(String(256))


class IdentifierEntity(Base):
    __tablename__ = 'identifier'
    id = Column(Integer, autoincrement=True, primary_key=True)
    identifier = Column(String(256), unique=True)
    md5 = Column(String(32))


class Storage:
    """数据库存储类"""

    def __init__(self):
        """初始化存储"""
        self._postgresql = SQL_URL
        self._engine = create_engine(self._postgresql)
        Base.metadata.create_all(self._engine)
        Session = sessionmaker(bind=self._engine)
        self._session = Session()

    def add_embedding(self, detail: str, embedding: list[float], url: str, title: str, author: str, identifier: str, channel: str):
        """添加新的嵌入向量"""
        self._session.add(EmbeddingEntity(detail=detail, embedding=embedding, url=url, title=title, author=author, identifier=identifier, channel=channel))
        self._session.commit()

    def add_all_embedding(self, embeddings: list[tuple[str, list[float], str, str, str, str, str]]):
        """添加多个嵌入向量"""
        data = [EmbeddingEntity(detail=detail, embedding=embedding, url=url, title=title, author=author, identifier=identifier, channel=channel)
                for detail, embedding, url, title, author, identifier, channel in embeddings]
        self._session.add_all(data)
        self._session.commit()

    def get_texts(self, embedding: list[float], limit=10) -> list[str]:
        """获取给定嵌入向量对应的文本"""
        result = self._session.query(EmbeddingEntity).order_by(
            EmbeddingEntity.embedding.cosine_distance(embedding)).limit(limit).all()
        return [(s.detail, s.title, s.url) for s in result]

    def clear(self):
        """清空数据库"""
        self._session.query(EmbeddingEntity).delete()
        self._session.commit()

    def __del__(self):
        """关闭session"""
        self._session.close()

    def add_identifier(self, identifier: str, md5: str):
        """添加新的 identifier """
        new_identifier = IdentifierEntity(identifier=identifier, md5=md5)
        self._session.add(new_identifier)
        self._session.commit()

    def search_identifier(self, identifier: str) -> Optional[dict]:
        """根据 identifier 查询"""
        result = self._session.query(IdentifierEntity).filter_by(identifier=identifier).first()
        if result:
            return {'identifier': result.identifier, 'md5': result.md5}
        else:
            return None

    def delete_identifier(self, identifier: str) -> bool:
        """根据 identifier 删除"""
        entity = self._session.query(IdentifierEntity).filter_by(identifier=identifier).first()
        if entity:
            self._session.delete(entity)
            self._session.commit()
            return True
        else:
            return False


if __name__ == '__main__':
    storage = Storage()
    storage.add_all_embedding([("test", [0]*1536, 'https://www.baidu.com', 'title', '@author')])
