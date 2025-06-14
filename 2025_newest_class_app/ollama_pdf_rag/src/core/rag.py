"""RAG 管道實現。"""
import logging
from typing import Any, Dict
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.multi_query import MultiQueryRetriever
from .llm import LLMManager

logger = logging.getLogger(__name__)

class RAGPipeline:
    """管理 RAG（檢索增強生成）管道。"""
    
    def __init__(self, vector_db: Any, llm_manager: LLMManager):
        self.vector_db = vector_db
        self.llm_manager = llm_manager
        self.retriever = self._setup_retriever()
        self.chain = self._setup_chain()
    
    def _setup_retriever(self) -> MultiQueryRetriever:
        """設置多查詢檢索器。"""
        try:
            return MultiQueryRetriever.from_llm(
                retriever=self.vector_db.as_retriever(),
                llm=self.llm_manager.llm,
                prompt=self.llm_manager.get_query_prompt()
            )
        except Exception as e:
            logger.error(f"Error setting up retriever: {e}")
            raise
    
    def _setup_chain(self) -> Any:
        """設置 RAG 鏈。"""
        try:
            return (
                {"context": self.retriever, "question": RunnablePassthrough()}
                | self.llm_manager.get_rag_prompt()
                | self.llm_manager.llm
                | StrOutputParser()
            )
        except Exception as e:
            logger.error(f"Error setting up chain: {e}")
            raise
    
    def get_response(self, question: str) -> str:
        """使用 RAG 管道獲取問題的回應。"""
        try:
            logger.info(f"Getting response for question: {question}")
            return self.chain.invoke(question)
        except Exception as e:
            logger.error(f"Error getting response: {e}")
            raise 