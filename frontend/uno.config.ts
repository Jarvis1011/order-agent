import { defineConfig, presetWind3 } from 'unocss'

export default defineConfig({
  presets: [presetWind3()],
  theme: {
    colors: {
      // 集中管理主色,之後想換品牌色只改這裡
      surface: {
        DEFAULT: '#0f1117',
        panel: '#161a23',
        raised: '#1e2330',
      },
      line: '#2a3040',
      accent: {
        DEFAULT: '#6366f1',
        soft: '#818cf8',
      },
    },
  },
})
