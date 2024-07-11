module.exports = {
  plugins: {
    'postcss-px-to-viewport': {
      viewportWidth: 750,  // 设计稿的视口宽度
      viewportHeight: 1334, // 设计稿的视口高度
      unitPrecision: 5,    // 转换后的精度，即小数点位数
      viewportUnit: 'vw',  // 转换成的视口单位
      selectorBlackList: ['.ignore', '.hairlines'], // 不需要转换的类
      minPixelValue: 1,    // 小于或等于1px不转换为视口单位
      mediaQuery: false,   // 允许在媒体查询中转换px
    },
  },
};
