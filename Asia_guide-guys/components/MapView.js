// components/MapView.js
import { useState, useEffect } from 'react';
import { Paper, Typography, Box, CircularProgress, Chip } from '@mui/material';
import styles from '../styles/MapView.module.css';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import ExploreIcon from '@mui/icons-material/Explore';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import HotelIcon from '@mui/icons-material/Hotel';
import LocalActivityIcon from '@mui/icons-material/LocalActivity';
import PublicIcon from '@mui/icons-material/Public';
import { useTranslation } from 'next-i18next';

// 模擬景點數據
const mockPOIData = {
  '東京': [
    { id: 1, name: '東京鐵塔', type: 'attraction', lat: 35.6586, lng: 139.7454 },
    { id: 2, name: '淺草寺', type: 'attraction', lat: 35.7147, lng: 139.7966 },
    { id: 3, name: '築地市場', type: 'food', lat: 35.6654, lng: 139.7707 },
    { id: 4, name: '明治神宮', type: 'attraction', lat: 35.6763, lng: 139.6993 },
    { id: 5, name: '六本木之丘', type: 'shopping', lat: 35.6604, lng: 139.7292 },
  ],
  '京都': [
    { id: 1, name: '清水寺', type: 'attraction', lat: 34.9949, lng: 135.7851 },
    { id: 2, name: '金閣寺', type: 'attraction', lat: 35.0394, lng: 135.7292 },
    { id: 3, name: '祇園', type: 'entertainment', lat: 35.0037, lng: 135.7751 },
    { id: 4, name: '伏見稻荷大社', type: 'attraction', lat: 34.9671, lng: 135.7727 },
    { id: 5, name: '京都站', type: 'transport', lat: 34.9858, lng: 135.7589 },
  ],
  '台北': [
    { id: 1, name: '台北101', type: 'attraction', lat: 25.0338, lng: 121.5646 },
    { id: 2, name: '故宮博物院', type: 'attraction', lat: 25.1022, lng: 121.5486 },
    { id: 3, name: '士林夜市', type: 'food', lat: 25.0879, lng: 121.5243 },
    { id: 4, name: '龍山寺', type: 'attraction', lat: 25.0374, lng: 121.4997 },
    { id: 5, name: '西門町', type: 'shopping', lat: 25.0428, lng: 121.5074 },
  ]
};

// 模擬天氣數據
const mockWeatherData = {
  '東京': { temp: 24, condition: '晴朗', humidity: 65, wind: 3.2 },
  '京都': { temp: 22, condition: '多雲', humidity: 70, wind: 2.8 },
  '台北': { temp: 28, condition: '部分多雲', humidity: 75, wind: 4.1 },
};

const MapView = ({ location = '東京' }) => {
  const [loading, setLoading] = useState(true);
  const [poiData, setPoiData] = useState([]);
  const [weatherData, setWeatherData] = useState(null);
  const [activePoiType, setActivePoiType] = useState('all');
  const { t } = useTranslation('common');

  useEffect(() => {
    // 模擬 API 載入
    setLoading(true);
    
    setTimeout(() => {
      // 設置景點數據
      const locationData = mockPOIData[location] || mockPOIData['東京'];
      setPoiData(locationData);
      
      // 設置天氣數據
      const weather = mockWeatherData[location] || mockWeatherData['東京'];
      setWeatherData(weather);
      
      setLoading(false);
    }, 1000);
  }, [location]);

  // 過濾 POI 數據
  const filteredPOIs = activePoiType === 'all' 
    ? poiData 
    : poiData.filter(poi => poi.type === activePoiType);

  // POI 類型選項
  const poiTypes = [
    { id: 'all', label: '全部', icon: <ExploreIcon fontSize="small" /> },
    { id: 'attraction', label: '景點', icon: <LocationOnIcon fontSize="small" /> },
    { id: 'food', label: '美食', icon: <RestaurantIcon fontSize="small" /> },
    { id: 'hotel', label: '住宿', icon: <HotelIcon fontSize="small" /> },
    { id: 'entertainment', label: '娛樂', icon: <LocalActivityIcon fontSize="small" /> },
  ];

  return (
    <div className={styles.mapView}>
      <Box className={styles.header}>
        <Typography variant="h5" className={styles.locationTitle}>
          <PublicIcon /> {location}
        </Typography>
        
        {weatherData && (
          <Paper className={styles.weatherCard}>
            <Typography variant="subtitle1">當前天氣</Typography>
            <Typography variant="h4">{weatherData.temp}°C</Typography>
            <Typography variant="body2">{weatherData.condition}</Typography>
            <Box mt={1}>
              <Typography variant="caption">
                濕度: {weatherData.humidity}% | 風速: {weatherData.wind} m/s
              </Typography>
            </Box>
          </Paper>
        )}
      </Box>

      <Box className={styles.poiFilter}>
        {poiTypes.map((type) => (
          <Chip
            key={type.id}
            icon={type.icon}
            label={type.label}
            onClick={() => setActivePoiType(type.id)}
            color={activePoiType === type.id ? 'primary' : 'default'}
            className={styles.filterChip}
          />
        ))}
      </Box>

      <Box className={styles.mapContainer}>
        {loading ? (
          <Box className={styles.loadingContainer}>
            <CircularProgress />
            <Typography variant="body2" mt={2}>載入地圖中...</Typography>
          </Box>
        ) : (
          <Paper className={styles.mapPlaceholder}>
            <Typography variant="body1" color="textSecondary">
              地圖視圖將在這裡顯示
            </Typography>
            <Typography variant="caption" color="textSecondary">
              整合 Google Maps API 即可顯示真實地圖
            </Typography>
          </Paper>
        )}
      </Box>

      <Box className={styles.poiList}>
        <Typography variant="h6" className={styles.poiListTitle}>
          {activePoiType === 'all' ? '熱門地點' : `${poiTypes.find(t => t.id === activePoiType)?.label || ''}`}
        </Typography>
        
        {loading ? (
          <CircularProgress size={20} />
        ) : (
          filteredPOIs.map((poi) => (
            <Paper key={poi.id} className={styles.poiItem}>
              {poi.type === 'attraction' && <LocationOnIcon color="primary" />}
              {poi.type === 'food' && <RestaurantIcon color="secondary" />}
              {poi.type === 'hotel' && <HotelIcon color="action" />}
              {poi.type === 'entertainment' && <LocalActivityIcon color="error" />}
              
              <Box ml={1}>
                <Typography variant="subtitle1">{poi.name}</Typography>
                <Typography variant="caption" color="textSecondary">
                  {poi.type === 'attraction' && '景點'}
                  {poi.type === 'food' && '美食'}
                  {poi.type === 'hotel' && '住宿'}
                  {poi.type === 'entertainment' && '娛樂'}
                  {poi.type === 'shopping' && '購物'}
                  {poi.type === 'transport' && '交通'}
                </Typography>
              </Box>
            </Paper>
          ))
        )}
      </Box>
    </div>
  );
};

export default MapView;