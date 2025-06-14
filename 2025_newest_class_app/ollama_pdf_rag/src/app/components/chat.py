"""用於 Streamlit 應用程式的聊天介面組件。"""
import streamlit as st
from typing import List, Dict

def init_chat_state():
    """如果不存在，初始化聊天狀態。"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def render_chat_interface(messages: List[Dict]):
    """使用消息歷史記錄渲染聊天介面。"""
    with st.container(height=500, border=True):
        # Display chat history
        for message in messages:
            avatar = "🤖" if message["role"] == "assistant" else "😎"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

def add_message(role: str, content: str):
    """將消息添加到聊天歷史記錄中。"""
    st.session_state.messages.append({"role": role, "content": content}) 