"""
智能會議記錄助手 - 網頁介面 (調試版)
使用Streamlit創建簡單易用的網頁界面，增加詳細錯誤處理
"""
import os
import time
import json
import asyncio
import threading
import streamlit as st
import traceback
import sys
from datetime import datetime
from dotenv import load_dotenv

# 配置頁面 - 必須是第一個 Streamlit 命令
st.set_page_config(
    page_title="會議記錄助手 (調試版)",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    .stButton button {
        width: 100%;
    }
    .speaker {
        font-weight: bold;
    }
    .timestamp {
        color: #888;
        font-size: 0.8em;
    }
    .action-item {
        background-color: #f0f7ff;
        border-left: 3px solid #2986cc;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .debug-log {
        font-family: monospace;
        font-size: 12px;
        color: #777;
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
        max-height: 300px;
        overflow-y: auto;
    }
    .recording-btn {
        background-color: #ff4b4b !important;
        color: white !important;
    }
    .recording-status {
        margin-top: 10px;
        margin-bottom: 20px;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .recording-active {
        background-color: #ffebee;
        color: #d32f2f;
        border: 1px solid #d32f2f;
    }
    .recording-inactive {
        background-color: #e8f5e9;
        color: #2e7d32;
        border: 1px solid #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

# 載入環境變數
load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 導入核心模組
try:
    from core.speech_to_text import SpeechToText
    from core.speaker_recognition import SpeakerRecognition
    from core.database import ConversationDatabase
    from core.openai_processor import OpenAIProcessor
except Exception as e:
    st.error(f"導入核心模組錯誤: {e}")
    st.code(traceback.format_exc())
    if not os.path.exists("core"):
        st.error("未找到核心模組目錄，請確保已創建core目錄並包含所需模組")

# 全局變量
recorder_thread = None
is_recording = False
speech_to_text_instance = None  # 用於保存SpeechToText實例，便於停止錄音

# 加入調試日誌功能
debug_log = []

def log_debug(message):
    """添加調試日誌"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    log_entry = f"[{timestamp}] {message}"
    debug_log.append(log_entry)
    print(log_entry)  # 同時輸出到控制台

# 初始化Session State - 確保所有必要的狀態變數都被正確初始化
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.transcript_entries = []
    st.session_state.is_recording = False
    st.session_state.meeting_data = None
    st.session_state.meeting_processed = False
    st.session_state.meeting_title = "未命名會議"
    st.session_state.participants = []
    st.session_state.enable_speaker_recognition = True
    st.session_state.enable_summary = True
    st.session_state.debug_log = []
    st.session_state.speaker_recognition_data = None
    st.session_state.mic_test_status = "False"
    st.session_state.has_microphone = False
    st.session_state.recording_stopped = False  # 新增：追蹤錄音是否已停止
    st.session_state.force_stop = False  # 新增：強制停止錄音的標記
    st.session_state.enable_transcription = True  # 新增：是否啟用文字轉錄功能

# 用於安全地更新Session State的鎖
session_state_lock = threading.RLock()

# 用於安全地更新Session State的函數
def update_session_state(key, value):
    with session_state_lock:
        st.session_state[key] = value
        log_debug(f"更新 session_state.{key}")

# 錄音函數 - 重新設計為更簡單的版本
def start_recording_thread(meeting_title, participants, enable_speaker_recognition, enable_transcription=True):
    """在背景線程中開始錄音"""
    global is_recording, speech_to_text_instance
    
    try:
        log_debug("啟動錄音線程")
        log_debug(f"會議標題: {meeting_title}")
        log_debug(f"參與者: {participants}")
        log_debug(f"啟用說話者識別: {enable_speaker_recognition}")
        log_debug(f"啟用文字轉錄: {enable_transcription}")
        
        # 如果啟用了文字轉錄，則初始化相關組件
        if enable_transcription:
            # 創建一個本地的SpeakerRecognition實例
            speaker_recognition = SpeakerRecognition()
            speaker_recognition.reset()
            speaker_recognition.set_meeting_info(meeting_title, participants)
            log_debug("SpeakerRecognition 實例已創建並初始化")
            
            # 保存到session state以便後續處理
            st.session_state.speaker_recognition_data = speaker_recognition
            
            # 初始化語音轉文字處理器 - 檢查模塊是否實現了同步方法
            log_debug(f"使用 Deepgram API 金鑰初始化 SpeechToText (金鑰長度: {len(DEEPGRAM_API_KEY) if DEEPGRAM_API_KEY else 0})")
            speech_to_text = SpeechToText(DEEPGRAM_API_KEY)
            speech_to_text_instance = speech_to_text  # 保存全局引用
            log_debug("SpeechToText 實例已創建")
            
            # 更詳細地顯示模塊方法
            log_debug(f"SpeechToText 方法: {dir(speech_to_text)}")
            
            # 定義回調函數
            def handle_transcript(transcript_data):
                """處理轉錄結果"""
                try:
                    log_debug(f"收到轉錄: {transcript_data.get('text', '')}")
                    
                    # 檢查是否需要強制停止
                    if st.session_state.force_stop:
                        log_debug("檢測到強制停止標記，不再處理轉錄")
                        return
                    
                    # 根據說話者識別設置處理
                    if enable_speaker_recognition:
                        processed_entry = speaker_recognition.handle_transcript(transcript_data)
                    else:
                        transcript_data["speaker_tag"] = None
                        processed_entry = speaker_recognition.handle_transcript(transcript_data)
                    
                    # 更新界面 - 安全地更新Session State
                    if transcript_data.get("is_final", False) and transcript_data.get("text", "").strip():
                        entries = speaker_recognition.get_full_transcript()
                        st.session_state.transcript_entries = entries.copy()
                        log_debug(f"更新轉錄條目，當前共 {len(entries)} 條")
                except Exception as e:
                    log_debug(f"處理轉錄回調錯誤: {e}")
                    log_debug(traceback.format_exc())
            
            # 啟動錄音
            is_recording = True
            st.session_state.is_recording = True
            st.session_state.recording_stopped = False
            log_debug("已設置錄音狀態為 True")
            
            # 檢查方法是否存在
            if hasattr(speech_to_text, 'start_recording_sync') and callable(speech_to_text.start_recording_sync):
                # 直接啟動錄音 - 同步方法
                log_debug("使用同步方法啟動錄音")
                speech_to_text.start_recording_sync(handle_transcript)
            else:
                # 使用異步方法
                log_debug("同步方法不存在，嘗試使用異步方法")
                # 創建新的事件循環
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # 定義異步主函數
                async def main_async():
                    try:
                        if hasattr(speech_to_text, 'start_recording') and callable(speech_to_text.start_recording):
                            log_debug("啟動異步錄音")
                            await speech_to_text.start_recording(handle_transcript)
                        else:
                            log_debug("錯誤: SpeechToText 模塊沒有實現 start_recording 或 start_recording_sync 方法")
                            raise NotImplementedError("SpeechToText 模塊沒有實現錄音方法")
                    except Exception as e:
                        log_debug(f"異步錄音過程中發生錯誤: {e}")
                        log_debug(traceback.format_exc())
                
                try:
                    # 運行異步主函數
                    loop.run_until_complete(main_async())
                finally:
                    # 關閉事件循環
                    loop.close()
                    log_debug("異步事件循環已關閉")
        else:
            # 只錄音模式 - 不進行文字轉錄
            log_debug("啟動只錄音模式 (不進行文字轉錄)")
            
            # 初始化錄音器 (使用PyAudio直接錄音)
            try:
                import pyaudio
                import wave
                import time
                from datetime import datetime
                
                # 設置錄音參數
                FORMAT = pyaudio.paInt16
                CHANNELS = 1
                RATE = 16000
                CHUNK = 1024
                
                # 創建錄音文件名
                now = datetime.now()
                date_str = now.strftime("%Y%m%d")
                time_str = now.strftime("%H%M%S")
                title_slug = meeting_title.replace(" ", "_")
                audio_filename = f"{title_slug}_{date_str}_{time_str}.wav"
                
                # 初始化PyAudio
                audio = pyaudio.PyAudio()
                
                # 開啟錄音流
                stream = audio.open(format=FORMAT, channels=CHANNELS,
                                   rate=RATE, input=True,
                                   frames_per_buffer=CHUNK)
                
                # 設置錄音狀態
                is_recording = True
                st.session_state.is_recording = True
                st.session_state.recording_stopped = False
                log_debug("已設置錄音狀態為 True (只錄音模式)")
                
                # 開始錄音
                frames = []
                log_debug(f"開始錄音到文件: {audio_filename}")
                
                # 錄音循環
                while is_recording and not st.session_state.force_stop:
                    data = stream.read(CHUNK)
                    frames.append(data)
                    time.sleep(0.01)  # 短暫休眠以減少CPU使用率
                
                # 停止錄音
                stream.stop_stream()
                stream.close()
                audio.terminate()
                
                # 保存錄音文件
                if frames:
                    wf = wave.open(audio_filename, 'wb')
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(audio.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()
                    log_debug(f"錄音已保存到文件: {audio_filename}")
                    
                    # 保存錄音文件路徑到session state
                    st.session_state.audio_filename = audio_filename
                else:
                    log_debug("未捕獲任何音頻數據")
            except Exception as e:
                log_debug(f"只錄音模式出錯: {e}")
                log_debug(traceback.format_exc())
        
        # 錄音結束
        log_debug("錄音線程結束")
        is_recording = False
        st.session_state.is_recording = False
        st.session_state.recording_stopped = True
        log_debug("已設置錄音狀態為 False")
    
    except Exception as e:
        log_debug(f"錄音線程出錯: {e}")
        log_debug(traceback.format_exc())
        is_recording = False
        st.session_state.is_recording = False
        st.session_state.recording_stopped = True

def stop_recording():
    """停止錄音"""
    global is_recording, speech_to_text_instance
    log_debug("停止錄音函數被調用")
    
    # 更新狀態
    is_recording = False
    st.session_state.is_recording = False
    st.session_state.force_stop = True
    
    try:
        # 嘗試直接停止SpeechToText實例
        if speech_to_text_instance is not None:
            log_debug("嘗試停止SpeechToText實例")
            log_debug(f"SpeechToText 方法: {dir(speech_to_text_instance)}")
            
            # 檢查stop_recording方法是否存在
            if hasattr(speech_to_text_instance, 'stop_recording') and callable(speech_to_text_instance.stop_recording):
                speech_to_text_instance.stop_recording()
                log_debug("SpeechToText實例已停止")
            else:
                log_debug("警告: SpeechToText模塊沒有stop_recording方法")
                
                # 強制終止錄音線程 - 最後的手段
                for thread in threading.enumerate():
                    if thread.name == "recorder_thread" and thread.is_alive():
                        log_debug(f"嘗試強制終止錄音線程: {thread.name}")
                        # 在Python中不能強制終止線程，但可以設置標記讓線程自行結束
                        # 我們已經設置了force_stop標記
        else:
            log_debug("SpeechToText實例不存在，無法停止")
    except Exception as e:
        log_debug(f"停止SpeechToText時出錯: {e}")
        log_debug(traceback.format_exc())
    
    log_debug("已設置錄音狀態為 False")
    
    # 添加臨時虛擬轉錄資料（測試用）
    if "transcript_entries" not in st.session_state or not st.session_state.transcript_entries:
        log_debug("添加臨時虛擬轉錄資料（測試用）")
        st.session_state.transcript_entries = [
            {"timestamp": "00:00:01", "speaker": "用戶1", "text": "這是一個測試會議。"},
            {"timestamp": "00:00:05", "speaker": "用戶2", "text": "我們可以測試摘要功能。"},
            {"timestamp": "00:00:10", "speaker": "用戶1", "text": "請幫我們生成一個簡短的摘要。"}
        ]
    
    # 添加成功信息
    st.success("錄音已停止！可以點擊「處理會議記錄」按鈕來分析會議內容，或使用「生成快速摘要」來直接獲取摘要。")
    
    # 如果有足夠的轉錄內容，提示用戶可以處理會議記錄
    if "transcript_entries" in st.session_state and len(st.session_state.transcript_entries) > 0:
        log_debug(f"錄音結束，有 {len(st.session_state.transcript_entries)} 條轉錄條目")
    else:
        log_debug("錄音結束，但沒有轉錄內容")

def process_meeting_results():
    """處理會議結果，生成摘要和行動項目"""
    log_debug("開始處理會議結果")
    
    # 從session state獲取speaker_recognition數據
    speaker_recognition = st.session_state.get("speaker_recognition_data")
    if not speaker_recognition:
        log_debug("錄音數據丟失，無法處理會議記錄")
        st.error("錄音數據丟失，無法處理會議記錄")
        return None
    
    # 獲取完整記錄文本
    transcript_text = speaker_recognition.get_formatted_transcript()
    log_debug(f"獲取到轉錄文本，字符數: {len(transcript_text)}")
    
    if not transcript_text.strip():
        log_debug("錄音結果為空，無法生成分析")
        st.error("錄音結果為空，無法生成分析")
        return None
    
    # 初始化AI處理器
    log_debug(f"初始化 OpenAIProcessor (API 金鑰長度: {len(OPENAI_API_KEY) if OPENAI_API_KEY else 0})")
    ai_processor = OpenAIProcessor(OPENAI_API_KEY)
    
    # 顯示處理進度
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 分析步驟
    status_text.text("正在處理會議記錄...")
    progress_bar.progress(10)
    time.sleep(0.5)
    
    # 生成摘要
    status_text.text("正在生成會議摘要...")
    progress_bar.progress(30)
    try:
        log_debug("開始生成會議摘要")
        summary = ai_processor.generate_summary(transcript_text)
        log_debug("會議摘要生成完成")
    except Exception as e:
        error_msg = f"生成摘要過程中出錯: {e}"
        log_debug(error_msg)
        log_debug(traceback.format_exc())
        st.error(error_msg)
        summary = "由於技術問題，無法生成摘要。"
    
    # 提取行動項目
    status_text.text("正在提取行動項目...")
    progress_bar.progress(60)
    try:
        log_debug("開始提取行動項目")
        action_items = ai_processor.extract_action_items(transcript_text)
        log_debug(f"提取到 {len(action_items)} 個行動項目")
    except Exception as e:
        error_msg = f"提取行動項目過程中出錯: {e}"
        log_debug(error_msg)
        log_debug(traceback.format_exc())
        st.error(error_msg)
        action_items = []
    
    # 獲取會議數據
    status_text.text("正在整理會議資料...")
    progress_bar.progress(80)
    transcript_entries = speaker_recognition.get_full_transcript()
    speaker_statistics = speaker_recognition.get_speaker_statistics()
    duration = speaker_recognition.get_meeting_duration()
    log_debug(f"會議持續時間: {duration}")
    
    # 初始化資料庫
    log_debug("初始化 ConversationDatabase")
    database = ConversationDatabase()
    
    # 創建會議記錄模式
    meeting_data = database.create_meeting_schema(
        title=st.session_state.meeting_title,
        participants=st.session_state.participants,
        transcript_entries=transcript_entries,
        speaker_statistics=speaker_statistics,
        duration=duration,
        summary=summary,
        action_items=action_items
    )
    log_debug("會議記錄結構已創建")
    
    # 保存到資料庫
    status_text.text("正在保存會議記錄...")
    progress_bar.progress(90)
    try:
        log_debug("嘗試保存會議記錄到資料庫")
        file_path = database.save_meeting(meeting_data)
        meeting_data["file_path"] = file_path
        log_debug(f"會議記錄已保存至: {file_path}")
    except Exception as e:
        error_msg = f"保存會議記錄時出錯: {e}"
        log_debug(error_msg)
        log_debug(traceback.format_exc())
        st.error(error_msg)
        meeting_data["file_path"] = "由於錯誤，未能保存檔案"
    
    # 更新進度
    progress_bar.progress(100)
    status_text.text("處理完成!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()
    log_debug("會議處理完成")
    
    return meeting_data

def export_report(meeting_data, format_type="markdown"):
    """匯出會議報告"""
    log_debug(f"匯出會議報告，格式: {format_type}")
    database = ConversationDatabase()
    content = database.export_meeting_record(meeting_data, format_type)
    
    # 構建檔案名稱
    title_slug = meeting_data.get("title", "未命名會議").replace(" ", "_")
    date_str = meeting_data.get("date", datetime.now().strftime("%Y%m%d"))
    ext = "md" if format_type == "markdown" else "json"
    file_name = f"{title_slug}_{date_str}.{ext}"
    log_debug(f"匯出檔案名稱: {file_name}")
    
    # 返回檔案內容和名稱
    return content, file_name

# 匯出摘要功能
def export_summary(meeting_data):
    """匯出會議摘要"""
    log_debug("匯出會議摘要")
    
    # 構建摘要內容
    summary = meeting_data.get("summary", "無法獲取摘要")
    title = meeting_data.get("title", "未命名會議")
    date = meeting_data.get("date", datetime.now().strftime("%Y-%m-%d"))
    participants = meeting_data.get("participants", [])
    participants_str = ", ".join(participants) if participants else "無參與者記錄"
    
    # 格式化摘要
    formatted_summary = f"""# {title} - 會議摘要
日期: {date}
參與者: {participants_str}

## 摘要內容

{summary}

## 行動項目

"""
    # 添加行動項目
    action_items = meeting_data.get("action_items", [])
    if action_items:
        for i, item in enumerate(action_items, 1):
            formatted_summary += f"{i}. {item}\n"
    else:
        formatted_summary += "無行動項目\n"
    
    # 構建檔案名稱
    title_slug = title.replace(" ", "_")
    date_str = date.replace("-", "")
    file_name = f"{title_slug}_摘要_{date_str}.txt"
    log_debug(f"匯出摘要檔案名稱: {file_name}")
    
    return formatted_summary, file_name

# 匯出選項區域
def display_export_options():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 匯出選項")
    
    # 檢查是否有處理過的會議數據
    has_meeting_data = "meeting_data" in st.session_state and st.session_state.meeting_data
    has_transcript = "transcript_entries" in st.session_state and len(st.session_state.transcript_entries) > 0
    
    if has_meeting_data:
        # 有處理過的會議數據 - 顯示完整匯出選項
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("匯出完整報告"):
                formatted_report, report_file_name = export_report(st.session_state.meeting_data)
                log_debug("準備下載完整報告")
                
                # 創建下載按鈕
                st.sidebar.download_button(
                    label="下載完整報告",
                    data=formatted_report,
                    file_name=report_file_name,
                    mime="text/plain"
                )
        with col2:
            if st.button("匯出摘要"):
                formatted_summary, summary_file_name = export_summary(st.session_state.meeting_data)
                log_debug("準備下載摘要")
                
                # 創建下載按鈕
                st.download_button(
                    label="下載摘要文件",
                    data=formatted_summary,
                    file_name=summary_file_name,
                    mime="text/plain"
                )
    elif has_transcript:
        # 有轉錄內容但尚未處理完整會議 - 提供快速摘要選項
        if st.button("生成快速摘要"):
            with st.spinner("正在生成摘要..."):
                summary = generate_quick_summary(st.session_state.transcript_entries)
                
                # 生成基本摘要文件
                now = datetime.now()
                title_slug = st.session_state.meeting_title.replace(" ", "_")
                date_str = now.strftime("%Y%m%d")
                time_str = now.strftime("%H%M%S")
                quick_summary_filename = f"{title_slug}_快速摘要_{date_str}_{time_str}.txt"
                
                formatted_summary = f"""# {st.session_state.meeting_title} - 快速摘要
生成時間: {now.strftime("%Y-%m-%d %H:%M:%S")}
參與者: {', '.join(st.session_state.participants)}

## 摘要內容

{summary}
"""
                
                # 創建下載按鈕
                st.download_button(
                    label="下載快速摘要",
                    data=formatted_summary,
                    file_name=quick_summary_filename,
                    mime="text/plain"
                )
    else:
        # 沒有處理過的會議數據，顯示禁用狀態
        st.info("完成錄音後，可以使用匯出功能")
        
        # 顯示禁用的按鈕（視覺提示）
        col1, col2 = st.columns(2)
        with col1:
            st.button("匯出完整報告", disabled=True)
        with col2:
            st.button("匯出摘要", disabled=True)

# 顯示API金鑰狀態 (只顯示是否存在，不顯示完整金鑰)
def display_api_status():
    if DEEPGRAM_API_KEY:
        st.sidebar.success("✅ Deepgram API 金鑰已設定")
    else:
        st.sidebar.error("❌ 缺少 Deepgram API 金鑰")

    if OPENAI_API_KEY:
        st.sidebar.success("✅ OpenAI API 金鑰已設定")
    else:
        st.sidebar.error("❌ 缺少 OpenAI API 金鑰")

# 添加快速摘要功能（無需處理完整會議）
def generate_quick_summary(transcript_entries):
    """生成快速摘要，不需要完整的會議處理流程"""
    log_debug("生成快速摘要")
    
    if not transcript_entries or len(transcript_entries) == 0:
        log_debug("轉錄內容為空，無法生成摘要")
        return "轉錄內容為空，無法生成摘要"
    
    # 構建完整的轉錄文本
    full_text = ""
    for entry in transcript_entries:
        speaker = entry.get("speaker", "未知說話者")
        text = entry.get("text", "")
        if text:
            full_text += f"{speaker}: {text}\n"
    
    if not full_text.strip():
        log_debug("處理後的轉錄文本為空")
        return "處理後的轉錄文本為空，無法生成摘要"
    
    try:
        # 檢查API密鑰是否存在
        if not OPENAI_API_KEY:
            log_debug("缺少OpenAI API密鑰")
            # 使用模擬摘要（用於測試）
            log_debug("使用模擬摘要")
            return """這是一個測試會議，主要討論了會議記錄助手的功能和使用方法。
參與者討論了如何使用摘要功能，以及如何從會議記錄中提取行動項目。
與會者一致認為這個功能非常有用，可以幫助團隊更有效地整理會議內容。"""
        
        # 初始化OpenAI處理器
        ai_processor = OpenAIProcessor(OPENAI_API_KEY)
        
        # 生成摘要
        summary = ai_processor.generate_summary(full_text)
        log_debug("快速摘要生成成功")
        return summary
    except Exception as e:
        error_msg = f"生成快速摘要時出錯: {e}"
        log_debug(error_msg)
        log_debug(traceback.format_exc())
        # 使用模擬摘要（出錯時的備用選項）
        log_debug("使用模擬摘要（由於錯誤）")
        return """這是一個模擬的會議摘要。

由於處理真實摘要時出現錯誤，系統生成了此模擬摘要。會議討論了多個議題，參與者分享了各自的觀點，並就某些問題達成了共識。

錯誤信息: """ + str(e)

# 顯示詳細操作說明
with st.expander("使用說明（如何錄音和產生摘要）"):
    st.markdown("""
    ### 如何使用會議記錄助手
    
    #### 錄音步驟
    1. 在側邊欄中設置會議標題和參與者名單
    2. 點擊「儲存設置」按鈕保存設置
    3. 點擊主頁面中的「開始錄音」按鈕開始錄音
    4. 系統會即時轉錄您的發言並顯示在會議記錄區域
    5. 錄音完成後，點擊「停止錄音」按鈕結束錄音
    
    #### 獲取摘要的兩種方式
    
    **方式一：快速摘要（較快）**
    1. 完成錄音後，點擊側邊欄「匯出選項」中的「生成快速摘要」按鈕
    2. 系統會快速生成摘要並提供下載選項
    
    **方式二：完整處理（更詳細）**
    1. 完成錄音後，點擊主頁面的「處理會議記錄」按鈕
    2. 系統會進行更全面的分析，包括摘要、行動項目和說話者統計
    3. 處理完成後，在側邊欄「匯出選項」中可以選擇匯出完整報告或只匯出摘要
    
    #### 常見問題
    - 如果錄音按鈕沒有正常工作，請檢查麥克風設置並使用「測試麥克風」功能
    - 如果界面出現問題，請嘗試重新加載頁面
    - 可以在「調試信息」區域檢查詳細的系統日誌
    """)

# 主界面
st.title("智能會議記錄助手 (調試版)")

# 顯示環境信息
st.info(f"Python 版本: {sys.version}")
try:
    import deepgram
    st.info(f"Deepgram SDK 版本: {deepgram.__version__}")
except:
    st.warning("無法確定 Deepgram SDK 版本")

# 錄音控制 - 重新設計為更直觀的界面
st.markdown("<h3>錄音控制</h3>", unsafe_allow_html=True)

# 顯示錄音狀態
if st.session_state.is_recording:
    st.markdown("""
    <div class="recording-status recording-active">
        🔴 正在錄音中... 請點擊下方「停止錄音」按鈕結束錄音
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="recording-status recording-inactive">
        ⚪ 未開始錄音
    </div>
    """, unsafe_allow_html=True)

# 添加模擬錄音選項（測試用）
use_mock_recording = st.checkbox("使用模擬錄音（測試用）", key="mock_recording")
if use_mock_recording:
    st.info("已啟用模擬錄音模式。點擊「開始錄音」和「停止錄音」將使用模擬數據，不會真正訪問麥克風。")

# 單一按鈕控制界面 - 根據當前狀態顯示不同按鈕
if st.session_state.is_recording:
    # 正在錄音中 - 顯示停止按鈕
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🛑 停止錄音", key="stop_recording", type="primary", use_container_width=True):
            log_debug("用戶點擊了停止錄音按鈕")
            stop_recording()
            st.rerun()
else:
    # 未錄音 - 顯示開始按鈕
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        start_button = st.button("🎙️ 開始錄音", key="start_recording", type="primary", use_container_width=True)
        if start_button:
            log_debug("用戶點擊了開始錄音按鈕")
            
            # 重置相關狀態
            st.session_state.force_stop = False
            
            if use_mock_recording:
                # 模擬錄音模式
                log_debug("使用模擬錄音模式")
                is_recording = True
                st.session_state.is_recording = True
                
                # 創建臨時的SpeakerRecognition實例
                speaker_recognition = SpeakerRecognition()
                speaker_recognition.reset()
                speaker_recognition.set_meeting_info(st.session_state.meeting_title, st.session_state.participants)
                st.session_state.speaker_recognition_data = speaker_recognition
                
                # 添加模擬轉錄數據
                st.session_state.transcript_entries = [
                    {"timestamp": "00:00:01", "speaker": "用戶1", "text": "這是一個模擬的會議記錄。"},
                    {"timestamp": "00:00:05", "speaker": "用戶2", "text": "我們可以測試摘要功能。"},
                    {"timestamp": "00:00:10", "speaker": "用戶1", "text": "請幫我們生成一個簡短的摘要。"},
                    {"timestamp": "00:00:15", "speaker": "用戶3", "text": "這個功能非常有用。"},
                    {"timestamp": "00:00:20", "speaker": "用戶2", "text": "我們還可以提取會議中的行動項目。"}
                ]
                st.rerun()
            else:
                # 真實錄音模式 - 啟動錄音線程
                recorder_thread = threading.Thread(
                    target=start_recording_thread,
                    args=(
                        st.session_state.meeting_title,
                        st.session_state.participants,
                        st.session_state.enable_speaker_recognition,
                        st.session_state.enable_transcription
                    ),
                    daemon=True,
                    name="recorder_thread"  # 添加線程名稱以便識別
                )
                log_debug("開始錄音線程已創建，準備啟動")
                recorder_thread.start()
                log_debug("開始錄音線程已啟動")
                st.rerun()

# 處理會議記錄按鈕 - 更明確的界面
if (not st.session_state.is_recording) and "transcript_entries" in st.session_state and st.session_state.transcript_entries:
    # 顯示一個分隔線
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 顯示處理選項
    st.markdown("<h3>處理轉錄內容</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 處理完整會議記錄
        if st.button("📊 處理完整會議記錄", key="process_meeting", use_container_width=True):
            log_debug("用戶點擊了處理會議記錄按鈕")
            with st.spinner("正在處理會議記錄..."):
                meeting_data = process_meeting_results()
                if meeting_data:
                    st.session_state.meeting_data = meeting_data
                    st.session_state.meeting_processed = True
                    log_debug("會議處理完成，刷新頁面")
                    st.success("會議記錄處理完成！")
                    st.rerun()
    
    with col2:
        # 生成快速摘要
        if st.button("📝 生成快速摘要", key="quick_summary", use_container_width=True):
            log_debug("用戶點擊了生成快速摘要按鈕")
            with st.spinner("正在生成摘要..."):
                summary = generate_quick_summary(st.session_state.transcript_entries)
                
                # 生成基本摘要文件
                now = datetime.now()
                title_slug = st.session_state.meeting_title.replace(" ", "_")
                date_str = now.strftime("%Y%m%d")
                time_str = now.strftime("%H%M%S")
                quick_summary_filename = f"{title_slug}_快速摘要_{date_str}_{time_str}.txt"
                
                formatted_summary = f"""# {st.session_state.meeting_title} - 快速摘要
生成時間: {now.strftime("%Y-%m-%d %H:%M:%S")}
參與者: {', '.join(st.session_state.participants)}

## 摘要內容

{summary}
"""
                st.session_state.quick_summary = formatted_summary
                st.session_state.quick_summary_filename = quick_summary_filename
                st.success("快速摘要生成完成！")
                
                # 直接顯示摘要
                st.subheader("快速摘要")
                st.markdown(summary)
                
                # 創建下載按鈕
                st.download_button(
                    label="下載快速摘要",
                    data=formatted_summary,
                    file_name=quick_summary_filename,
                    mime="text/plain",
                    key="download_quick_summary"
                )

# 麥克風測試 - 改進麥克風測試功能
if not st.session_state.is_recording:
    if st.button("測試麥克風", key="test_mic"):
        log_debug("用戶點擊了測試麥克風按鈕")
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            log_debug(f"PyAudio 初始化成功，版本: {pyaudio.get_portaudio_version_text() if hasattr(pyaudio, 'get_portaudio_version_text') else pyaudio.get_portaudio_version()}")
            
            # 獲取音訊設備信息
            info = p.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            
            # 列出所有麥克風
            mic_list = []
            for i in range(0, numdevices):
                device_info = p.get_device_info_by_host_api_device_index(0, i)
                if device_info.get('maxInputChannels') > 0:
                    mic_info = device_info
                    mic_list.append(f"索引 {i}: {mic_info.get('name')} (通道: {mic_info.get('maxInputChannels')})")
                    log_debug(f"檢測到麥克風: {mic_info.get('name')}")
            
            # 嘗試找到默認輸入設備
            try:
                default_input = p.get_default_input_device_info()
                log_debug(f"默認輸入設備: {default_input.get('name', '未知')} (索引: {default_input.get('index', '未知')})")
                st.info(f"默認麥克風: {default_input.get('name', '未知')}")
            except Exception as e:
                log_debug(f"獲取默認麥克風時出錯: {e}")
                st.warning("無法獲取默認麥克風信息")
            
            # 設置麥克風狀態
            st.session_state.mic_test_status = "True"
            
            # 釋放資源
            p.terminate()
            
            if mic_list:
                st.success(f"檢測到 {len(mic_list)} 個麥克風")
                for mic in mic_list:
                    st.write(f"• {mic}")
                st.session_state.has_microphone = True
            else:
                st.error("未檢測到任何麥克風！請檢查您的設備連接。")
                log_debug("未檢測到麥克風")
                st.session_state.has_microphone = False
                
            # 添加幫助信息
            st.info("如果麥克風測試正常但無法錄音，請嘗試以下步驟：\n"
                    "1. 確保已授予瀏覽器麥克風訪問權限\n"
                    "2. 檢查系統聲音設置中是否啟用了麥克風\n"
                    "3. 如果使用耳機或外部麥克風，請確保正確連接")
        
        except ImportError:
            st.error("缺少PyAudio庫，無法測試麥克風")
            st.info("請安裝PyAudio：pip install pyaudio")
            log_debug("缺少PyAudio庫")
        except Exception as e:
            error_msg = f"測試麥克風時出錯: {e}"
            st.error(error_msg)
            log_debug(error_msg)
            log_debug(traceback.format_exc())

# 顯示轉錄內容
st.header("會議記錄")

# 實時顯示轉錄內容
transcript_container = st.container()
with transcript_container:
    if "transcript_entries" in st.session_state:
        for entry in st.session_state.transcript_entries:
            timestamp = entry.get("timestamp", "")
            speaker = entry.get("speaker", "未知說話者")
            text = entry.get("text", "")
            
            st.markdown(f"""
            <div class="transcript-entry">
                <span class="timestamp">[{timestamp}]</span> 
                <span class="speaker">{speaker}:</span> {text}
            </div>
            """, unsafe_allow_html=True)

# 顯示處理結果
if st.session_state.meeting_processed and st.session_state.meeting_data:
    meeting_data = st.session_state.meeting_data
    
    st.header("會議報告")
    
    # 基本信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("會議標題", meeting_data.get("title", "未命名會議"))
    with col2:
        st.metric("日期", meeting_data.get("date", "未知"))
    with col3:
        st.metric("持續時間", meeting_data.get("duration", "未知"))
    
    # 參與者
    st.subheader("參與者")
    st.write(", ".join(meeting_data.get("participants", ["未知"])))
    
    # 摘要
    st.subheader("會議摘要")
    st.write(meeting_data.get("summary", "未生成摘要"))
    
    # 行動項目
    st.subheader("行動項目")
    if meeting_data.get("action_items"):
        for item in meeting_data.get("action_items"):
            assignee = f" (@{item.get('assignee', '未分配')})" if item.get('assignee') else ""
            deadline = f" - 截止日期: {item.get('deadline')}" if item.get('deadline') else ""
            st.markdown(f"""
            <div class="action-item">
                {item.get('action')}{assignee}{deadline}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("無行動項目")
    
    # 說話者統計
    st.subheader("說話者統計")
    
    # 使用圖表顯示統計數據
    if meeting_data.get("speaker_statistics"):
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            
            # 創建數據框
            stats_data = []
            for speaker, stats in meeting_data.get("speaker_statistics", {}).items():
                stats_data.append({
                    "說話者": speaker,
                    "發言次數": stats["sentences"],
                    "總字數": stats["total_words"],
                    "發言時間(秒)": stats["speaking_time"]
                })
            
            df = pd.DataFrame(stats_data)
            
            # 顯示數據表
            st.dataframe(df)
            
            # 圖表列
            chart_col1, chart_col2 = st.columns(2)
            
            # 發言次數圖表
            with chart_col1:
                fig, ax = plt.subplots()
                ax.bar(df["說話者"], df["發言次數"], color="skyblue")
                ax.set_title("發言次數")
                ax.set_ylabel("次數")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            
            # 發言時間圖表
            with chart_col2:
                fig, ax = plt.subplots()
                ax.bar(df["說話者"], df["發言時間(秒)"], color="lightgreen")
                ax.set_title("發言時間")
                ax.set_ylabel("秒")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
        except Exception as e:
            st.error(f"生成圖表時出錯: {e}")
            log_debug(f"生成圖表時出錯: {e}")
            log_debug(traceback.format_exc())
            # 顯示原始數據
            st.json(meeting_data.get("speaker_statistics", {}))
    else:
        st.write("無說話者統計數據")

# 調試區域 (可折疊)
with st.expander("顯示調試信息"):
    st.subheader("調試日誌")
    
    # 顯示所有日誌
    log_entries = debug_log + st.session_state.get("debug_log", [])
    if log_entries:
        st.markdown(f"""
        <div class="debug-log">
            {'<br>'.join(log_entries)}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.write("暫無調試日誌")
    
    # 系統信息
    st.subheader("系統信息")
    st.json({
        "Python版本": sys.version,
        "操作系統": os.name,
        "執行路徑": os.getcwd(),
        "有Deepgram密鑰": bool(DEEPGRAM_API_KEY),
        "有OpenAI密鑰": bool(OPENAI_API_KEY),
    })
    
    # 顯示session_state內容
    st.subheader("Session State")
    session_state_info = {k: str(v) if k != "speaker_recognition_data" else "SpeakerRecognition實例" 
                          for k, v in st.session_state.items()}
    st.json(session_state_info)
    
    # 按鈕清空日誌
    if st.button("清空調試日誌"):
        debug_log.clear()
        st.session_state.debug_log = []
        st.success("調試日誌已清空")
        st.rerun()  # 使用 st.rerun() 代替已棄用的 experimental_rerun()

# 頁腳
st.markdown("---")
st.caption("© 2025 智能會議記錄助手 | 由 Deepgram 和 OpenAI 技術提供支持")

# 側邊欄 - 會議設置
with st.sidebar:
    st.header("會議設置")
    
    # 會議標題
    meeting_title = st.text_input("會議標題", value=st.session_state.get("meeting_title", "未命名會議"))
    
    # 參與者列表
    participants_str = st.text_area("參與者 (每行一個名稱)", value="\n".join(st.session_state.get("participants", [])))
    
    # 功能選項
    st.subheader("功能選項")
    
    # 新增：是否啟用文字轉錄
    enable_transcription = st.checkbox("啟用文字轉錄", value=st.session_state.get("enable_transcription", True), 
                                     help="取消勾選將只進行錄音，不進行文字轉錄和摘要生成")
    
    # 說話者識別
    enable_speaker_recognition = st.checkbox("啟用說話者識別", value=st.session_state.get("enable_speaker_recognition", True),
                                          help="自動識別不同說話者")
    
    # 摘要生成
    enable_summary = st.checkbox("啟用摘要生成", value=st.session_state.get("enable_summary", True),
                              help="自動生成會議摘要和提取行動項目")
    
    # 保存設置按鈕
    if st.button("儲存設置"):
        # 更新會議標題
        st.session_state.meeting_title = meeting_title
        
        # 更新參與者列表
        participants = [p.strip() for p in participants_str.split("\n") if p.strip()]
        st.session_state.participants = participants
        
        # 更新功能選項
        st.session_state.enable_transcription = enable_transcription
        st.session_state.enable_speaker_recognition = enable_speaker_recognition
        st.session_state.enable_summary = enable_summary
        
        st.success("設置已保存！")