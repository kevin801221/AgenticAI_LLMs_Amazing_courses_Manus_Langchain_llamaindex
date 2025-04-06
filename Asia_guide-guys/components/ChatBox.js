// components/ChatBox.js
import { useState } from 'react';
import styles from '../styles/ChatBox.module.css';
import { Avatar, Paper, CircularProgress, TextField, IconButton, Box, Typography } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import MicIcon from '@mui/icons-material/Mic';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ReactMarkdown from 'react-markdown';

const ChatBox = ({ messages, isTyping, onSendMessage, endRef }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);

  // 處理消息發送
  const handleSendMessage = () => {
    if (inputMessage.trim() && !isTyping) {
      onSendMessage(inputMessage);
      setInputMessage('');
    }
  };

  // 處理按鍵事件
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // 處理語音輸入
  const handleVoiceInput = () => {
    // 檢查瀏覽器是否支持語音識別
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.lang = 'zh-TW';
      recognition.continuous = false;
      recognition.interimResults = false;
      
      recognition.onstart = () => {
        setIsRecording(true);
      };
      
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage((prev) => prev + transcript);
      };
      
      recognition.onerror = (event) => {
        console.error('語音識別錯誤:', event.error);
        setIsRecording(false);
      };
      
      recognition.onend = () => {
        setIsRecording(false);
      };
      
      recognition.start();
    } else {
      alert('您的瀏覽器不支持語音識別功能');
    }
  };

  // 渲染歡迎消息
  const renderWelcomeMessage = () => (
    <div className={styles.welcomeMessage}>
      <Typography variant="h4" gutterBottom>
        歡迎使用亞洲旅遊助手
      </Typography>
      <Typography variant="body1" paragraph>
        我是您的AI旅遊顧問，可以幫助您規劃亞洲之旅、了解當地文化、查詢天氣和交通信息等。
      </Typography>
      <Typography variant="body1">
        您可以問我關於亞洲旅遊的任何問題，例如：
      </Typography>
      <Box sx={{ mt: 2, mb: 2 }}>
        <Typography variant="body2" sx={{ fontStyle: 'italic', mb: 1 }}>
          "請推薦京都的文化景點"
        </Typography>
        <Typography variant="body2" sx={{ fontStyle: 'italic', mb: 1 }}>
          "我想了解泰國的傳統節日"
        </Typography>
        <Typography variant="body2" sx={{ fontStyle: 'italic', mb: 1 }}>
          "幫我規劃5天的東京旅行行程"
        </Typography>
        <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
          "從首爾到釜山的交通方式有哪些？"
        </Typography>
      </Box>
    </div>
  );

  return (
    <div className={styles.chatBox}>
      <div className={styles.messagesContainer}>
        {messages.length === 0 ? (
          renderWelcomeMessage()
        ) : (
          messages.map((message) => (
            <div 
              key={message.id} 
              className={`${styles.messageRow} ${message.sender === 'user' ? styles.userMessageRow : styles.botMessageRow}`}
            >
              <div className={styles.avatarContainer}>
                {message.sender === 'user' ? (
                  <Avatar className={styles.userAvatar}>
                    <PersonIcon />
                  </Avatar>
                ) : (
                  <Avatar className={styles.botAvatar}>
                    <SmartToyIcon />
                  </Avatar>
                )}
              </div>
              <Paper 
                className={`${styles.messageBubble} ${message.sender === 'user' ? styles.userMessage : styles.botMessage}`}
              >
                <ReactMarkdown>{message.content}</ReactMarkdown>
                <Typography variant="caption" className={styles.timestamp}>
                  {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </Typography>
              </Paper>
            </div>
          ))
        )}
        
        {isTyping && (
          <div className={`${styles.messageRow} ${styles.botMessageRow}`}>
            <div className={styles.avatarContainer}>
              <Avatar className={styles.botAvatar}>
                <SmartToyIcon />
              </Avatar>
            </div>
            <Paper className={`${styles.messageBubble} ${styles.typingIndicator}`}>
              <CircularProgress size={20} sx={{ mr: 1 }} />
              <Typography variant="body2">正在思考...</Typography>
            </Paper>
          </div>
        )}
        
        <div ref={endRef} />
      </div>

      <Paper className={styles.inputContainer}>
        <TextField
          fullWidth
          placeholder="輸入您的旅遊問題..."
          variant="outlined"
          multiline
          maxRows={4}
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isTyping}
          className={styles.inputField}
        />
        <Box className={styles.inputButtons}>
          <IconButton 
            color={isRecording ? 'error' : 'primary'} 
            onClick={handleVoiceInput}
            disabled={isTyping}
          >
            <MicIcon />
          </IconButton>
          <IconButton 
            color="primary" 
            onClick={handleSendMessage} 
            disabled={!inputMessage.trim() || isTyping}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>
    </div>
  );
};

export default ChatBox;