"""LLM 配置和設置。"""
import logging
from langchain_ollama.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate

logger = logging.getLogger(__name__)

class LLMManager:
    """管理 LLM 配置和提示。"""
    
    def __init__(self, model_name: str = "llama2"):
        self.model_name = model_name
        self.llm = ChatOllama(model=model_name)
        
    def get_query_prompt(self) -> PromptTemplate:
        """獲取查詢生成提示。"""
        return PromptTemplate(
            input_variables=["question"],
            template="""您是一個 AI 語言模型助理。您的任務是產生 2 個
            不同版本的用戶問題，以從向量數據庫中檢索相關文件。
            通過產生用戶問題的多種角度，您的目標是幫助用戶克服
            基於距離的相似度搜索的一些限制。請提供這些用換行分隔的替代問題。
            原始問題: {question}"""
        )
    
    def get_rag_prompt(self) -> ChatPromptTemplate:
        """獲取 RAG 提示模板。"""
        template = """僅根據以下上下文回答問題：
        {context}
        問題： {question}
        """
        return ChatPromptTemplate.from_template(template) 