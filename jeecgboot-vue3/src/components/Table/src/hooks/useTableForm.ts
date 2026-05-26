import type { ComputedRef, Slots } from 'vue';
import type { BasicTableProps, FetchParams } from '../types/table';
import { unref, computed } from 'vue';
import type { FormProps } from '/@/components/Form';
import { isFunction } from '/@/utils/is';

export function useTableForm(
  propsRef: ComputedRef<BasicTableProps>,
  slots: Slots,
  fetch: (opt?: FetchParams | undefined) => Promise<void>,
  getLoading: ComputedRef<boolean | undefined>
) {
  const getFormProps = computed((): Partial<FormProps> => {
    const { formConfig } = unref(propsRef);
    const { submitButtonOptions, autoSubmitOnEnter} = formConfig || {};
    return {
      showAdvancedButton: true,
      // 默认搜索区布局：1 行 2 个搜索字段 + 操作按钮组（查询/重置/高级筛选），
      // 第 3 个起自动折叠进"高级筛选"。每字段 1/3 宽度（span 8），
      // 2 字段 + actionCol(8) = 24，刚好一行。
      // 页面通过 formConfig.autoAdvancedCol / baseColProps 可覆盖此默认。
      autoAdvancedCol: 2,
      baseColProps: { xs: 24, sm: 24, md: 12, lg: 8, xl: 8, xxl: 8 },
      ...formConfig,
      submitButtonOptions: { loading: unref(getLoading), ...submitButtonOptions },
      compact: true,
      // 代码逻辑说明: [issues/568]设置 autoSubmitOnEnter: false 不生效 ---
      autoSubmitOnEnter: autoSubmitOnEnter,
    };
  });

  const getFormSlotKeys: ComputedRef<string[]> = computed(() => {
    const keys = Object.keys(slots);
    return keys.map((item) => (item.startsWith('form-') ? item : null)).filter((item) => !!item) as string[];
  });

  function replaceFormSlotKey(key: string) {
    if (!key) return '';
    return key?.replace?.(/form\-/, '') ?? '';
  }

  function handleSearchInfoChange(info: Recordable) {
    const { handleSearchInfoFn } = unref(propsRef);
    if (handleSearchInfoFn && isFunction(handleSearchInfoFn)) {
      info = handleSearchInfoFn(info) || info;
    }
    fetch({ searchInfo: info, page: 1 });
  }

  return {
    getFormProps,
    replaceFormSlotKey,
    getFormSlotKeys,
    handleSearchInfoChange,
  };
}
