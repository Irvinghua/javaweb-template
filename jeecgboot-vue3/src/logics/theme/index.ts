import { getThemeColors, generateColors } from '../../../build/config/themeConfig';
import {
  replaceStyleVariables,
  loadDarkThemeCss,
  replaceCssColors,
  darkCssIsReady,
  linkID,
  styleTagId,
  appendCssToDom,
  getStyleDom,
} from '@rys-fe/vite-plugin-theme/es/client';
import { mixLighten, mixDarken, tinycolor } from '@rys-fe/vite-plugin-theme/es/colorUtils';
import { useAppStore } from '/@/store/modules/app';
import { defHttp } from '/@/utils/http/axios';

let cssText = '';

/** Sync the --accent CSS variable layer with the new primary color */
function syncAccentVars(color: string) {
  try {
    const tc = (window as any).__tinycolor__ ? (window as any).__tinycolor__(color) : null;
    const root = document.documentElement;
    root.style.setProperty('--accent', color);
    // Derive lighter shades by mixing with white
    // --accent-50: very light (92% white mix)
    root.style.setProperty('--accent-50', blendWithWhite(color, 0.92));
    // --accent-100: light (80% white mix)
    root.style.setProperty('--accent-100', blendWithWhite(color, 0.80));
    // --accent-600: slightly darker (15% darken)
    root.style.setProperty('--accent-600', darkenColor(color, 15));
    // --accent-700: darker (25%)
    root.style.setProperty('--accent-700', darkenColor(color, 25));
  } catch (e) {
    // fallback: just set --accent
    document.documentElement.style.setProperty('--accent', color);
  }
}

function blendWithWhite(hex: string, ratio: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  const rr = Math.round(r + (255 - r) * ratio);
  const gg = Math.round(g + (255 - g) * ratio);
  const bb = Math.round(b + (255 - b) * ratio);
  return `rgb(${rr},${gg},${bb})`;
}

function darkenColor(hex: string, percent: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  const factor = 1 - percent / 100;
  const rr = Math.round(r * factor);
  const gg = Math.round(g * factor);
  const bb = Math.round(b * factor);
  return `rgb(${rr},${gg},${bb})`;
}

export async function changeTheme(color: string) {
  // 代码逻辑说明: 【QQYUN-6366】升级到antd4.x
  const appStore = useAppStore();
  appStore.setProjectConfig({ themeColor: color });
  // Immediately sync --accent CSS variables layer
  syncAccentVars(color);
  const colors = generateColors({
    mixDarken,
    mixLighten,
    tinycolor,
    color,
  });
  // 代码逻辑说明: 【QQYUN-8570】生产环境暗黑模式下主题色不生效
  if (import.meta.env.PROD && appStore.getDarkMode === 'dark') {
    if (!darkCssIsReady && !cssText) {
      await loadDarkThemeCss();
    }
    const el: HTMLLinkElement = document.getElementById(linkID) as HTMLLinkElement;
    if (el?.href) {
      // cssText = await fetchCss(el.href) as string;
      !cssText && (cssText = await defHttp.get({ url: el.href }, { isTransformResponse: false }));
      const colorVariables = [...getThemeColors(color), ...colors];
      const processCss = await replaceCssColors(cssText, colorVariables);
      appendCssToDom(getStyleDom(styleTagId) as HTMLStyleElement, processCss);
    }
  } else {
    await replaceStyleVariables({
      colorVariables: [...getThemeColors(color), ...colors],
    });
    fixDark();
  }
}
// 【LOWCOD-2262】修复黑暗模式下切换皮肤无效的问题
async function fixDark() {
  // 代码逻辑说明: 【QQYUN-8570】生产环境暗黑模式下主题色不生效
  const el = document.getElementById(styleTagId);
  if (el) {
    el.innerHTML = el.innerHTML.replace(/\\["']dark\\["']/g, `'dark'`);
  }
}
