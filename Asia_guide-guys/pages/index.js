// pages/index.js
import Head from 'next/head';
import { useState, useEffect, useRef } from 'react';
import styles from '../styles/Home.module.css';
import ChatBox from '../components/ChatBox';
import MapView from '../components/MapView';
import Sidebar from '../components/Sidebar';
import UserPreferences from '../components/UserPreferences';
import { useTranslation } from 'next-i18next';
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [userPreferences, setUserPreferences] = useState({
    language: 'zh-TW',
    location: '',
    interests: [],
    budget: 'medium',
  });
  const [showMap, setShowMap] = useState(false);
  const chatEndRef = useRef(null);
  const { t } = useTranslation('common');

  // 滾動到最新消息
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // 載入用戶偏好設置
  useEffect(() => {
    const storedPreferences = localStorage.getItem('userPreferences');
    if (storedPreferences) {
      setUserPreferences(JSON.parse(storedPreferences));
    }
  }, []);

  // 保存用戶偏好設置
  const savePreferences = (newPreferences) => {
    setUserPreferences(newPreferences);
    localStorage.setItem('userPreferences', JSON.stringify(newPreferences));
    setShowPreferences(false);
  };

  // 發送消息
  const sendMessage = async (content) => {
    if (!content.trim()) return;

    // 添加用戶消息
    const userMessage = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setIsTyping(true);

    try {
      // 模擬 API 調用
      setTimeout(() => {
        const botResponse = {
          id: (Date.now() + 1).toString(),
          content: generateBotResponse(content, userPreferences),
          sender: 'bot',
          timestamp: new Date().toISOString(),
        };
        setMessages((prevMessages) => [...prevMessages, botResponse]);
        setIsTyping(false);
      }, 1500);
    } catch (error) {
      console.error('Error sending message:', error);
      setIsTyping(false);
    }
  };

  // 模擬機器人回應
  const generateBotResponse = (userMessage, preferences) => {
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('你好') || lowerMessage.includes('嗨') || lowerMessage.includes('hi')) {
      return `您好！我是您的亞洲旅遊助手，很高興為您服務。我可以幫助您規劃旅遊行程、提供景點推薦、回答文化問題，以及提供即時的旅遊資訊。您想了解哪個亞洲目的地呢？`;
    }
    
    if (lowerMessage.includes('天氣') || lowerMessage.includes('weather')) {
      return `根據最新天氣預報，${preferences.location || '您所在的位置'}今天天氣晴朗，溫度在24-28°C之間，非常適合出遊。明天可能有輕微降雨，建議攜帶雨具。`;
    }
    
    if (lowerMessage.includes('推薦') || lowerMessage.includes('景點')) {
      const location = preferences.location || '台北';
      return `根據您的興趣（${preferences.interests.join('、') || '文化歷史、美食探索'}），我推薦您在${location}可以訪問以下景點：
1. 文化歷史博物館 - 展示當地豐富的文化遺產
2. 傳統市場 - 體驗當地生活和品嚐美食
3. 城市公園 - 欣賞美麗的自然風景
4. 歷史古蹟 - 了解當地的歷史發展

您想了解更多關於哪個景點的信息？`;
    }
    
    if (lowerMessage.includes('行程') || lowerMessage.includes('itinerary')) {
      return `以下是為您準備的一日行程安排：
      
上午 9:00 - 參觀當地博物館
上午 11:30 - 前往傳統市場，品嚐當地美食午餐
下午 13:30 - 探訪歷史街區
下午 16:00 - 城市公園漫步
晚上 18:00 - 享用特色晚餐
晚上 20:00 - 欣賞夜景或文化表演

這個行程如何？您可以根據自己的偏好進行調整。`;
    }
    
    return `謝謝您的提問。我正在搜索相關的信息，並結合您的偏好（${preferences.interests.join('、') || '未設置'}）為您提供最合適的建議。您還有其他問題嗎？`;
  };

  // 清除對話
  const clearConversation = () => {
    setMessages([]);
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>{t('title')}</title>
        <meta name="description" content={t('description')} />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <Sidebar 
          onOpenPreferences={() => setShowPreferences(true)}
          onClearChat={clearConversation}
          onToggleMap={() => setShowMap(!showMap)}
        />
        
        <div className={styles.contentArea}>
          {showMap ? (
            <MapView location={userPreferences.location || '東京'} />
          ) : (
            <ChatBox 
              messages={messages}
              isTyping={isTyping}
              onSendMessage={sendMessage}
              endRef={chatEndRef}
            />
          )}
        </div>
      </main>

      {showPreferences && (
        <UserPreferences 
          preferences={userPreferences}
          onSave={savePreferences}
          onClose={() => setShowPreferences(false)}
        />
      )}
    </div>
  );
}

export async function getServerSideProps(context) {
  const locale = context.locale || 'zh-TW';
  
  return {
    props: {
      ...(await serverSideTranslations(locale, ['common'])),
    },
  };
}