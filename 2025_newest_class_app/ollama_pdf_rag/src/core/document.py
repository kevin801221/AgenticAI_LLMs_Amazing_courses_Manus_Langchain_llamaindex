"""文件處理功能。"""
import logging
from pathlib import Path
from typing import List
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """處理 PDF 文件的載入和處理。"""
    
    def __init__(self, chunk_size: int = 7500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def load_pdf(self, file_path: Path) -> List:
        """載入 PDF 文件。"""
        try:
            logger.info(f"Loading PDF from {file_path}")
            loader = UnstructuredPDFLoader(str(file_path))
            return loader.load()
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise
    
    def split_documents(self, documents: List) -> List:
        """將文件分割成區塊。"""
        try:
            logger.info("Splitting documents into chunks")
            return self.splitter.split_documents(documents)
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            raise 