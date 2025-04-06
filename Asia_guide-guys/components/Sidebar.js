// components/Sidebar.js
import { useState } from 'react';
import styles from '../styles/Sidebar.module.css';
import { 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  Drawer, 
  IconButton, 
  Divider, 
  Typography,
  Box
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import SettingsIcon from '@mui/icons-material/Settings';
import DeleteIcon from '@mui/icons-material/Delete';
import MapIcon from '@mui/icons-material/Map';
import ChatIcon from '@mui/icons-material/Chat';
import InfoIcon from '@mui/icons-material/Info';
import HistoryIcon from '@mui/icons-material/History';
import TranslateIcon from '@mui/icons-material/Translate';
import { useTranslation } from 'next-i18next';

const Sidebar = ({ onOpenPreferences, onClearChat, onToggleMap }) => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const { t } = useTranslation('common');

  const toggleDrawer = (open) => (event) => {
    if (
      event.type === 'keydown' &&
      (event.key === 'Tab' || event.key === 'Shift')
    ) {
      return;
    }
    setDrawerOpen(open);
  };

  const menuItems = [
    {
      text: t('sidebar.settings'),
      icon: <SettingsIcon />,
      onClick: () => {
        onOpenPreferences();
        setDrawerOpen(false);
      },
    },
    {
      text: t('sidebar.clearChat'),
      icon: <DeleteIcon />,
      onClick: () => {
        onClearChat();
        setDrawerOpen(false);
      },
    },
    {
      text: t('sidebar.toggleMap'),
      icon: <MapIcon />,
      onClick: () => {
        onToggleMap();
        setDrawerOpen(false);
      },
    },
    {
      text: t('sidebar.history'),
      icon: <HistoryIcon />,
      onClick: () => {
        alert('旅行歷史功能即將推出');
        setDrawerOpen(false);
      },
    },
    {
      text: t('sidebar.language'),
      icon: <TranslateIcon />,
      onClick: () => {
        alert('語言切換功能即將推出');
        setDrawerOpen(false);
      },
    },
    {
      text: t('sidebar.about'),
      icon: <InfoIcon />,
      onClick: () => {
        alert('亞洲觀光機器人是基於最新大型語言模型(LLM)技術的智慧旅遊助手，專為亞洲地區旅遊設計。');
        setDrawerOpen(false);
      },
    },
  ];

  return (
    <>
      <div className={styles.menuButton}>
        <IconButton 
          color="primary" 
          aria-label="open drawer" 
          onClick={toggleDrawer(true)}
          size="large"
        >
          <MenuIcon />
        </IconButton>
      </div>

      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={toggleDrawer(false)}
      >
        <Box
          className={styles.drawerContent}
          role="presentation"
        >
          <Box className={styles.drawerHeader}>
            <Typography variant="h6" className={styles.title}>
              {t('appName')}
            </Typography>
            <ChatIcon color="primary" fontSize="large" />
          </Box>
          
          <Divider />
          
          <List>
            {menuItems.map((item) => (
              <ListItem button key={item.text} onClick={item.onClick}>
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItem>
            ))}
          </List>
          
          <Divider />
          
          <Box className={styles.drawerFooter}>
            <Typography variant="caption" color="textSecondary">
              © 2025 亞洲觀光機器人
            </Typography>
            <Typography variant="caption" color="textSecondary">
              版本 1.0.0
            </Typography>
          </Box>
        </Box>
      </Drawer>
    </>
  );
};

export default Sidebar;