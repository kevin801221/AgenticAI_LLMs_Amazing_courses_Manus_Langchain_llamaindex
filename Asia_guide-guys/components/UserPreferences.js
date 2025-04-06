// components/UserPreferences.js
import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Box,
  Typography,
  Slider,
  Autocomplete,
  FormHelperText,
} from '@mui/material';
import { useTranslation } from 'next-i18next';

// 語言選項
const languageOptions = [
  { value: 'zh-TW', label: '繁體中文' },
  { value: 'zh-CN', label: '簡體中文' },
  { value: 'en', label: 'English' },
  { value: 'ja', label: '日本語' },
  { value: 'ko', label: '한국어' },
];

// 興趣選項
const interestOptions = [
  '文化歷史',
  '美食探索',
  '自然風景',
  '購物體驗',
  '冒險活動',
  '藝術博物館',
  '傳統節慶',
  '溫泉療養',
  '宗教寺廟',
  '現代建築',
  '夜生活',
  '海灘度假',
  '主題公園',
  '鄉村體驗',
  '攝影景點',
];

// 亞洲主要城市
const asianCities = [
  '東京',
  '京都',
  '大阪',
  '首爾',
  '釜山',
  '台北',
  '高雄',
  '香港',
  '澳門',
  '上海',
  '北京',
  '廣州',
  '深圳',
  '曼谷',
  '清邁',
  '普吉島',
  '新加坡',
  '吉隆坡',
  '河內',
  '胡志明市',
  '馬尼拉',
  '雅加達',
  '巴厘島',
  '德里',
  '孟買',
];

// 預算標記
const budgetMarks = [
  { value: 0, label: '經濟' },
  { value: 50, label: '中等' },
  { value: 100, label: '豪華' },
];

// 將預算值轉換為文本
const getBudgetText = (value) => {
  if (value <= 25) return 'economy';
  if (value <= 75) return 'medium';
  return 'luxury';
};

// 將預算文本轉換為值
const getBudgetValue = (text) => {
  switch (text) {
    case 'economy': return 0;
    case 'medium': return 50;
    case 'luxury': return 100;
    default: return 50;
  }
};

const UserPreferences = ({ preferences, onSave, onClose }) => {
  const [localPreferences, setLocalPreferences] = useState({
    language: 'zh-TW',
    location: '',
    interests: [],
    budget: 'medium',
  });
  
  const { t } = useTranslation('common');
  
  // 當對話框打開時，從上下文加載偏好設置
  useEffect(() => {
    setLocalPreferences({
      ...preferences,
    });
  }, [preferences]);
  
  // 處理輸入變化
  const handleChange = (field, value) => {
    setLocalPreferences((prev) => ({
      ...prev,
      [field]: value,
    }));
  };
  
  // 處理預算滑塊變化
  const handleBudgetChange = (_, value) => {
    handleChange('budget', getBudgetText(value));
  };
  
  // 保存偏好設置
  const handleSave = () => {
    onSave(localPreferences);
  };

  return (
    <Dialog open={true} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>{t('preferences.title')}</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="textSecondary" paragraph>
          {t('preferences.description')}
        </Typography>
        
        {/* 語言選擇 */}
        <FormControl fullWidth sx={{ mb: 3, mt: 2 }}>
          <InputLabel>{t('preferences.language')}</InputLabel>
          <Select
            value={localPreferences.language}
            label={t('preferences.language')}
            onChange={(e) => handleChange('language', e.target.value)}
          >
            {languageOptions.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
          <FormHelperText>{t('preferences.languageHelp')}</FormHelperText>
        </FormControl>
        
        {/* 位置輸入 */}
        <FormControl fullWidth sx={{ mb: 3 }}>
          <Autocomplete
            value={localPreferences.location}
            onChange={(_, newValue) => handleChange('location', newValue)}
            options={asianCities}
            renderInput={(params) => (
              <TextField {...params} label={t('preferences.location')} />
            )}
            freeSolo
          />
          <FormHelperText>{t('preferences.locationHelp')}</FormHelperText>
        </FormControl>
        
        {/* 興趣選擇 */}
        <FormControl fullWidth sx={{ mb: 3 }}>
          <Autocomplete
            multiple
            value={localPreferences.interests}
            onChange={(_, newValue) => handleChange('interests', newValue)}
            options={interestOptions}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  label={option}
                  {...getTagProps({ index })}
                  color="primary"
                  variant="outlined"
                />
              ))
            }
            renderInput={(params) => (
              <TextField {...params} label={t('preferences.interests')} placeholder={t('preferences.interestsPlaceholder')} />
            )}
          />
          <FormHelperText>{t('preferences.interestsHelp')}</FormHelperText>
        </FormControl>
        
        {/* 預算滑塊 */}
        <FormControl fullWidth sx={{ mb: 3 }}>
          <Typography id="budget-slider" gutterBottom>
            {t('preferences.budget')}
          </Typography>
          <Slider
            value={getBudgetValue(localPreferences.budget)}
            onChange={handleBudgetChange}
            aria-labelledby="budget-slider"
            marks={budgetMarks}
            step={null}
            valueLabelDisplay="off"
          />
          <FormHelperText>{t('preferences.budgetHelp')}</FormHelperText>
        </FormControl>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{t('common.cancel')}</Button>
        <Button onClick={handleSave} variant="contained" color="primary">
          {t('common.save')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default UserPreferences;