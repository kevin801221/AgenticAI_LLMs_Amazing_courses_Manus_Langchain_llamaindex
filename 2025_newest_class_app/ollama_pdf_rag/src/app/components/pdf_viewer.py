"""用於 Streamlit 應用程式的 PDF 檢視器組件。"""
import streamlit as st
import pdfplumber
from pathlib import Path
from typing import List, Optional

def extract_pdf_images(pdf_path: Path) -> List:
    """從 PDF 頁面中提取圖像。"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return [page.to_image().original for page in pdf.pages]
    except Exception as e:
        st.error(f"Error extracting PDF images: {e}")
        return []

def render_pdf_viewer(pdf_pages: Optional[List] = None):
    """渲染帶有縮放控制的 PDF 檢視器。"""
    if pdf_pages:
        # PDF display controls
        zoom_level = st.slider(
            "Zoom Level",
            min_value=100,
            max_value=1000,
            value=700,
            step=50
        )
        
        # Display PDF pages
        with st.container(height=410, border=True):
            for page_image in pdf_pages:
                st.image(page_image, width=zoom_level) 