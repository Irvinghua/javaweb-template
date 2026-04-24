import type { App } from 'vue';
import { warn } from '/@/utils/log';

// 该工程已移除 @jeecg/online 在线表单/列表设计器。
// 原先通过 lazyPackages 懒加载外部包，现在保留兼容 API 但不再注册任何包。

// noinspection JSUnusedGlobalSymbols
const installOptions = {
  baseImport,
};

export function registerPackages(_app: App) {
  // no-op：不再注册任何外部模块
}

/**
 * 外部包组件按需加载（保留接口签名以兼容 routeHelper 的调用）。
 * 当前工程没有外部动态包，直接返回 null。
 */
export async function loadPackageComponent(_component: string): Promise<(() => Promise<Recordable>) | null> {
  return null;
}

// 模块里可使用的import
const importGlobs = [import.meta.glob('../../utils/**/*.{ts,js,tsx}'), import.meta.glob('../../hooks/**/*.{ts,js,tsx}')];

/**
 * 基础项目导包
 * 目前支持导入如下
 * /@/utils/**
 * /@/hooks/**
 *
 * @param path 文件路径，ts无需输入后缀名。如：/@/utils/common/compUtils
 */
async function baseImport(path: string) {
  if (path) {
    // 将 /@/ 替换成 ../../
    path = path.replace(/^\/@\//, '../../');
    for (const glob of importGlobs) {
      for (const key of Object.keys(glob)) {
        if (path === key || `${path}.ts` === key || `${path}.tsx` === key) {
          return glob[key]();
        }
      }
    }
    warn(`引入失败：${path} 不存在`);
  }
  return null;
}

// 避免未使用告警
void installOptions;
