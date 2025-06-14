"""用於 Streamlit 應用程式的側邊欄組件。"""
import streamlit as st
import ollama

def render_sidebar():
    """渲染帶有模型選擇和控制的側邊欄。"""
    with st.sidebar:
        st.subheader("Model Settings")
        
        # Get available models
        try:
            models_info = ollama.list()
            available_models = tuple(model["name"] for model in models_info["models"])
            
            # Model selection
            selected_model = st.selectbox(
                "Select Model",
                available_models,
                index=0 if available_models else None,
                help="選擇本地 Ollama 模型"
            )
            
            return selected_model
            
        except Exception as e:
            st.error(f"Error loading models: {e}")
            return None 