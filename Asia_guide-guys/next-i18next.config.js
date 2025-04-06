// next-i18next.config.js
module.exports = {
    i18n: {
      defaultLocale: 'zh-TW',
      locales: ['zh-TW', 'zh-CN', 'en', 'ja', 'ko'],
      localeDetection: true,
    },
    localePath: 'public/locales',
    reloadOnPrerender: process.env.NODE_ENV === 'development',
  };