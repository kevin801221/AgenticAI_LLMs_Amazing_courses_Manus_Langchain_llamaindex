# venv 已經 activate 的前提下
# python -m streamlit run run.py

# 導入必要的函式庫
import streamlit as st  # Streamlit 用於建立網頁應用程式介面
from langchain_groq import ChatGroq  # Groq 的 LLM 聊天模型
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper  # arXiv 和 Wikipedia API 包裝器
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun  # arXiv 和 Wikipedia 查詢工具
from langchain.agents import initialize_agent, AgentType  # LangChain 代理初始化和類型
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler  # Streamlit 回調處理器
import os  # 作業系統相關功能
from dotenv import load_dotenv  # 載入環境變數

# 載入 .env 檔案中的環境變數
load_dotenv()

# 從環境變數中獲取 Groq API 金鑰
api_key = os.getenv("GROQ_API_KEY")

# 設定 arXiv API 包裝器
# top_k_results=1: 只返回最相關的1個結果
# doc_content_chars_max=200: 限制文檔內容最多200個字符
arxiv_wrapper = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=200)
# 建立 arXiv 查詢工具
arxiv = ArxivQueryRun(api_wrapper=arxiv_wrapper)

# 設定 Wikipedia API 包裝器
# 參數設定與 arXiv 相同
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)
# 建立 Wikipedia 查詢工具
wiki = WikipediaQueryRun(api_wrapper=api_wrapper)

# 設定 Streamlit 應用程式標題
st.title("🔎Search Web with Llama 3.3")

# 初始化 Streamlit 會話狀態中的訊息列表
# 如果 "messages" 不存在於會話狀態中，則建立一個包含初始助手訊息的列表
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi, I can search the web. How can I help you?"}
    ]

# 顯示所有歷史訊息
# 遍歷會話狀態中的所有訊息並顯示在聊天介面中
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg['content'])

# 建立聊天輸入框並處理用戶輸入
# 當用戶輸入訊息時，將其添加到會話狀態並顯示
if prompt := st.chat_input(placeholder="Enter Your Question Here"):
    # 將用戶訊息添加到會話狀態
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 在聊天介面中顯示用戶訊息
    st.chat_message("user").write(prompt)

    # 初始化 Groq 聊天模型
    # groq_api_key: 使用從環境變數獲取的 API 金鑰
    # model_name: 指定使用的模型名稱
    # streaming: 啟用流式輸出
    llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.3-70b-versatile", streaming=True)
    
    # 定義可用的工具列表
    # 包含 arXiv 和 Wikipedia 查詢工具
    tools = [arxiv, wiki]

    # 初始化搜尋代理
    # tools: 代理可使用的工具列表
    # llm: 使用的語言模型
    # agent: 代理類型，使用零次學習反應描述型代理
    # handle_parsing_errors: 啟用解析錯誤處理
    search_agent = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
        handle_parsing_errors=True
    )

    # 在助手訊息容器中處理回應
    with st.chat_message("assistant"):
        # 建立 Streamlit 回調處理器
        # st.container(): 建立一個新的容器來顯示代理的思考過程
        # expand_new_thoughts=False: 不自動展開新的思考步驟
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        
        try:
            # 執行搜尋代理
            # 傳入用戶的提示作為輸入
            # callbacks: 使用 Streamlit 回調處理器來顯示執行過程
            response = search_agent.run(prompt, callbacks=[st_cb])
            
            # 將助手的回應添加到會話狀態
            st.session_state.messages.append({'role': 'assistant', "content": response})
            
            # 在聊天介面中顯示回應
            st.write(response)
            
        except ValueError as e:
            # 捕獲並顯示任何值錯誤
            # 這通常發生在代理無法解析回應或遇到其他處理錯誤時
            st.error(f"An error occurred: {e}")