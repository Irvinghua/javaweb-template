<template>
  <div class="table-settings">
    <!-- 刷新按钮 -->
    <RedoSetting v-if="getSetting.redo" :isMobile="isMobile" :getPopupContainer="getTableContainer" />

    <!-- 设置齿轮按钮：合并 密度 + 列设置 + 全屏 -->
    <a-popover
      v-if="getSetting.size || getSetting.setting || getSetting.fullScreen"
      v-model:open="settingPopVisible"
      placement="bottomRight"
      trigger="click"
      overlayClassName="table-settings-gear-popover"
      :getPopupContainer="getTableContainer"
    >
      <template #content>
        <div class="tsp-inner">
          <!-- 密度设置 -->
          <div v-if="getSetting.size" class="tsp-section">
            <div class="tsp-label">
              <AppstoreOutlined />
              密度
            </div>
            <div class="tsp-seg">
              <button :class="{ active: currentSize === 'large' }" @click="setSize('large')">宽松</button>
              <button :class="{ active: currentSize === 'middle' }" @click="setSize('middle')">默认</button>
              <button :class="{ active: currentSize === 'small' }" @click="setSize('small')">紧凑</button>
            </div>
          </div>

          <!-- 列设置 -->
          <div v-if="getSetting.setting" class="tsp-section">
            <div class="tsp-label">
              <UnorderedListOutlined />
              列显示
            </div>
            <div class="tsp-col-control">
              <label class="tsp-col-row tsp-col-header">
                <a-checkbox
                  :indeterminate="colIndeterminate"
                  v-model:checked="colCheckAll"
                  @change="onCheckAllChange"
                />
                <span>全选</span>
                <a-checkbox
                  v-if="!isTreeTable"
                  v-model:checked="checkIndex"
                  @change="handleIndexCheckChange"
                  style="margin-left: auto"
                >序号</a-checkbox>
              </label>
            </div>
            <div class="tsp-columns" ref="columnListRef">
              <a-checkbox-group v-model:value="checkedList" @change="onColChange">
                <template v-for="item in plainOptions" :key="item.value">
                  <label
                    class="tsp-col-row"
                    v-if="!('ifShow' in item && !item.ifShow)"
                  >
                    <DragOutlined class="tsp-drag-icon" />
                    <a-checkbox :value="item.value">{{ item.label }}</a-checkbox>
                  </label>
                </template>
              </a-checkbox-group>
            </div>
            <div class="tsp-foot">
              <button @click="resetColumns">重置</button>
              <button @click="doSaveColumnSetting" class="tsp-save">保存</button>
            </div>
          </div>

          <!-- 全屏开关 -->
          <div v-if="getSetting.fullScreen" class="tsp-section tsp-fullscreen-row">
            <div class="tsp-label">
              <FullscreenOutlined v-if="!isFullscreen" />
              <FullscreenExitOutlined v-else />
              全屏
            </div>
            <a-switch :checked="isFullscreen" @change="toggleFullscreen" size="small" />
          </div>
        </div>
      </template>

      <!-- 触发按钮：齿轮图标 -->
      <Tooltip placement="top">
        <template #title>设置</template>
        <SettingOutlined class="table-settings-gear-icon" />
      </Tooltip>
    </a-popover>
  </div>
</template>
<script lang="ts">
  import type { PropType } from 'vue';
  import type { TableSetting, ColumnChangeParam, SizeType } from '../../types/table';
  import type { BasicColumn } from '../../types/table';
  import type { CheckboxChangeEvent } from 'ant-design-vue/lib/checkbox/interface';
  import { defineComponent, computed, unref, ref, reactive, toRefs, watchEffect, nextTick, watch } from 'vue';
  import { Tooltip } from 'ant-design-vue';
  import {
    SettingOutlined,
    AppstoreOutlined,
    UnorderedListOutlined,
    DragOutlined,
    FullscreenOutlined,
    FullscreenExitOutlined,
  } from '@ant-design/icons-vue';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { useTableContext } from '../../hooks/useTableContext';
  import { useColumnsCache } from '../../hooks/useColumnsCache';
  import { useFullscreen } from '@vueuse/core';
  import { useRoute } from 'vue-router';
  import { createLocalStorage } from '/@/utils/cache';
  import { isNullAndUnDef } from '/@/utils/is';
  import { cloneDeep } from 'lodash-es';
  import Sortablejs from 'sortablejs';
  import type Sortable from 'sortablejs';
  import RedoSetting from './RedoSetting.vue';
  import { useLocaleStoreWithOut } from '/@/store/modules/locale';

  interface ColState {
    checkAll: boolean;
    isInit?: boolean;
    checkedList: string[];
    defaultCheckList: string[];
  }

  interface Options {
    label: string;
    value: string;
    fixed?: boolean | 'left' | 'right';
    [key: string]: any;
  }

  export default defineComponent({
    name: 'TableSetting',
    components: {
      RedoSetting,
      Tooltip,
      SettingOutlined,
      AppstoreOutlined,
      UnorderedListOutlined,
      DragOutlined,
      FullscreenOutlined,
      FullscreenExitOutlined,
    },
    props: {
      setting: {
        type: Object as PropType<TableSetting>,
        default: () => ({}),
      },
      mode: String,
    },
    emits: ['columns-change'],
    setup(props, { emit }) {
      const { t } = useI18n();
      const table = useTableContext();
      const $ls = createLocalStorage();
      const route = useRoute();
      const localeStore = useLocaleStoreWithOut();

      // ── popover visibility ───────────────────────────────────────────
      const settingPopVisible = ref(false);

      // ── computed settings ────────────────────────────────────────────
      const getSetting = computed((): TableSetting => ({
        redo: true,
        size: true,
        setting: true,
        fullScreen: false,
        ...props.setting,
      }));

      const isMobile = computed(() => props.mode === 'mobile');

      function getTableContainer() {
        return table ? unref(table.wrapRef) : document.body;
      }

      // ── density ──────────────────────────────────────────────────────
      const currentSize = ref<SizeType>(table.getSize());
      const cacheKey = computed(() => {
        const path = route.path;
        let key = path.replace(/[/\\]/g, '_');
        const ck = table.getBindValues.value.tableSetting?.cacheKey;
        if (ck) key += ':' + ck;
        return 'tableSizeCache:' + key;
      });
      const cachedSize: SizeType | null = $ls.get(cacheKey.value);
      if (cachedSize) {
        currentSize.value = cachedSize;
        table.setProps({ size: cachedSize });
      }

      // 同时给 table.wrapRef 挂 density class，避免依赖 AntD size 类（AntD4 对 'large' 不一定加类）
      function applyDensityClass(size: SizeType) {
        const wrap = unref(table.wrapRef);
        if (!wrap || !wrap.classList) return;
        wrap.classList.remove('jeecg-table-density-loose', 'jeecg-table-density-compact');
        if (size === 'large') wrap.classList.add('jeecg-table-density-loose');
        else if (size === 'small') wrap.classList.add('jeecg-table-density-compact');
      }

      function setSize(size: SizeType) {
        currentSize.value = size;
        table.setProps({ size });
        $ls.set(cacheKey.value, size);
        applyDensityClass(size);
      }

      // 初始化时（缓存值或默认值）也同步一下 class
      nextTick(() => applyDensityClass(unref(currentSize)));

      // ── fullscreen ───────────────────────────────────────────────────
      const { toggle: toggleFullscreen, isFullscreen } = useFullscreen(table.wrapRef);

      // ── column setting ───────────────────────────────────────────────
      const isTreeTable = computed(() => table.getBindValues.value.isTreeTable);
      const getColumnsRef = table.getColumnsRef();

      const cachePlainOptions = ref<Options[]>([]);
      const plainOptions = ref<Options[]>([]);
      const plainSortOptions = ref<Options[]>([]);
      const columnListRef = ref<any>(null);
      const restAfterOptions = { value: null as any };

      const colState = reactive<ColState>({
        checkAll: true,
        checkedList: [],
        defaultCheckList: [],
      });
      const checkIndex = ref(false);

      // sortable (must be declared before useColumnsCache which references it via closure)
      let sortable: Sortable;
      const sortableOrder = ref<string[]>();
      let inited = false;

      // forward declarations so useColumnsCache can reference them
      function setColumns(columns: BasicColumn[] | string[]) {
        table.setColumns(columns);
        const data: ColumnChangeParam[] = unref(plainSortOptions).map((col) => {
          const visible =
            columns.findIndex(
              (c: BasicColumn | string) =>
                c === col.value || (typeof c !== 'string' && c.dataIndex === col.value)
            ) !== -1;
          return { dataIndex: col.value, fixed: col.fixed, visible };
        });
        emit('columns-change', data);
      }

      function handleColumnFixed(item: BasicColumn, fixed?: 'left' | 'right') {
        if (!colState.checkedList.includes(item.dataIndex as string)) return;
        const columns = getColumnsLocal() as BasicColumn[];
        const isFixed = item.fixed === fixed ? false : fixed;
        const idx = columns.findIndex((col) => col.dataIndex === item.dataIndex);
        if (idx !== -1) columns[idx].fixed = isFixed;
        item.fixed = isFixed;
        if (isFixed && !item.width) item.width = 100;
        table.setCacheColumnsByField?.(item.dataIndex as string, { fixed: isFixed });
        setColumns(columns);
      }

      const { saveSetting, resetSetting, getCache } = useColumnsCache(
        {
          state: colState,
          popoverVisible: settingPopVisible,
          plainOptions,
          plainSortOptions,
          sortableOrder,
          checkIndex,
          restAfterOptions,
        },
        setColumns,
        handleColumnFixed
      );

      function doSaveColumnSetting() {
        saveSetting();
      }

      const colIndeterminate = computed(() => {
        const len = plainOptions.value.length;
        const checkedLen = colState.checkedList.length;
        return checkedLen > 0 && checkedLen < len;
      });

      function getColumnsLocal(): Options[] {
        const ret: Options[] = [];
        let cols = table.getColumns({ ignoreIndex: true, ignoreAction: true, ignoreAuth: true, ignoreIfShow: true });
        if (!cols.length) cols = table.getCacheColumns();
        cols.forEach((item) => {
          ret.push({
            label: (item.title as string) || (item.customTitle as string),
            value: (item.dataIndex || item.title) as string,
            ...item,
          });
        });
        return ret;
      }

      async function init() {
        const columns = getColumnsLocal();
        const checkList = table
          .getColumns({ ignoreAction: true, ignoreIndex: true, ignoreAuth: true, ignoreIfShow: true })
          .map((item) => {
            if (item.defaultHidden) return '';
            return item.dataIndex || item.title;
          })
          .filter(Boolean) as string[];

        const { sortedList = [] } = getCache() || {};
        await nextTick();
        if (!plainOptions.value.length) {
          let tmp = columns;
          if (sortedList?.length) {
            tmp = columns.sort((prev, next) => sortedList.indexOf(prev.value) - sortedList.indexOf(next.value));
          }
          plainOptions.value = tmp;
          plainSortOptions.value = tmp;
          cachePlainOptions.value = tmp;
          colState.defaultCheckList = checkList;
        } else {
          unref(plainOptions).forEach((item: BasicColumn) => {
            const findItem = columns.find((col: BasicColumn) => col.dataIndex === item.dataIndex);
            if (findItem) item.fixed = findItem.fixed;
          });
          if (sortedList?.length) {
            plainOptions.value.sort((prev, next) => sortedList.indexOf(prev.value) - sortedList.indexOf(next.value));
          }
        }
        colState.isInit = true;
        colState.checkedList = checkList;
        colState.checkAll = columns.length === checkList.length;
      }

      watchEffect(() => {
        setTimeout(() => {
          if (!colState.isInit) init();
        }, 0);
      });

      watchEffect(() => {
        const values = unref(table?.getBindValues) || {};
        checkIndex.value = !!values.showIndexColumn;
      });

      watch([localeStore], () => {
        const columns = getColumnsLocal();
        plainOptions.value = columns;
        plainSortOptions.value = columns;
        cachePlainOptions.value = columns;
      });

      watch([getColumnsRef], () => {
        init();
      });

      // initialize sortable when gear popover opens
      watch(settingPopVisible, (visible) => {
        if (visible && !inited) {
          setTimeout(() => {
            const el = columnListRef.value;
            if (!el) return;
            sortable = Sortablejs.create(el, {
              animation: 500,
              delay: 400,
              delayOnTouchOnly: true,
              handle: '.tsp-drag-icon',
              onEnd: (evt) => {
                const { oldIndex, newIndex } = evt;
                if (isNullAndUnDef(oldIndex) || isNullAndUnDef(newIndex) || oldIndex === newIndex) return;
                const cols = cloneDeep(plainSortOptions.value);
                if (oldIndex! > newIndex!) {
                  cols.splice(newIndex!, 0, cols[oldIndex!]);
                  cols.splice(oldIndex! + 1, 1);
                } else {
                  cols.splice(newIndex! + 1, 0, cols[oldIndex!]);
                  cols.splice(oldIndex!, 1);
                }
                plainSortOptions.value = cols;
                const colKeys = cols.map((item) => item.value);
                const arr = colKeys.filter((cItem) => colState.checkedList.find((lItem) => lItem === cItem));
                setColumns(arr);
                restAfterOptions.value = null;
              },
            });
            if (!sortableOrder.value) {
              sortableOrder.value = sortable.toArray();
            }
            inited = true;
          }, 500);
        }
      });

      function onCheckAllChange(e: CheckboxChangeEvent) {
        const checkList = plainOptions.value.map((item) => item.value);
        if (e.target.checked) {
          colState.checkedList = checkList;
          setColumns(checkList);
        } else {
          colState.checkedList = [];
          setColumns([]);
        }
      }

      function onColChange(checkedList: string[]) {
        const len = plainSortOptions.value.length;
        colState.checkAll = checkedList.length === len;
        const sortList = unref(plainSortOptions).map((item) => item.value);
        checkedList.sort((prev, next) => sortList.indexOf(prev) - sortList.indexOf(next));
        setColumns(checkedList);
      }

      function resetColumns() {
        setColumns(table.getCacheColumns());
        setTimeout(() => {
          colState.checkedList = table
            .getColumns({ ignoreAction: true, ignoreAuth: true, ignoreIfShow: true })
            .map((item) => item.dataIndex || item.title)
            .filter(Boolean) as string[];
          colState.checkAll = true;
          plainOptions.value = unref(cachePlainOptions);
          plainSortOptions.value = unref(cachePlainOptions);
          restAfterOptions.value = getColumnsLocal();
          if (sortableOrder.value) sortable?.sort(sortableOrder.value);
          resetSetting();
        }, 100);
      }

      function handleIndexCheckChange(e: CheckboxChangeEvent) {
        table.setProps({ showIndexColumn: e.target.checked });
      }

      return {
        getSetting,
        t,
        isMobile,
        getTableContainer,
        settingPopVisible,
        // density
        currentSize,
        setSize,
        // fullscreen
        isFullscreen,
        toggleFullscreen,
        // column
        isTreeTable,
        columnListRef,
        plainOptions,
        ...toRefs(colState),
        colCheckAll: computed({
          get: () => colState.checkAll,
          set: (v) => { colState.checkAll = v; },
        }),
        colIndeterminate,
        checkIndex,
        onCheckAllChange,
        onColChange,
        resetColumns,
        doSaveColumnSetting,
        handleIndexCheckChange,
      };
    },
  });
</script>
<style lang="less">
  /* ── table-settings 容器 ── */
  .table-settings {
    display: flex;
    align-items: center;
    gap: 8px;

    svg {
      width: 1.2em;
      height: 1.2em;
    }

    /* Redo 图标 */
    .anticon-redo,
    .anticon-loading {
      cursor: pointer;
      font-size: 16px;
      color: var(--ink-500);
      padding: 6px;
      border-radius: 8px;
      border: 1px solid var(--line);
      background: var(--surface);
      transition: background-color var(--fast), color var(--fast);

      &:hover {
        background: var(--surface-2);
        color: var(--ink-900);
      }
    }

    /* 齿轮图标 */
    .table-settings-gear-icon {
      cursor: pointer;
      font-size: 16px;
      color: var(--ink-500);
      padding: 6px;
      border-radius: 8px;
      border: 1px solid var(--line);
      background: var(--surface);
      transition: background-color var(--fast), color var(--fast);
      display: inline-flex;
      align-items: center;
      justify-content: center;

      &:hover {
        background: var(--surface-2);
        color: var(--ink-900);
      }
    }
  }

  /* ── 设置浮层 ── */
  .table-settings-gear-popover {
    .ant-popover-inner {
      padding: 0;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: var(--shadow-pop);
      min-width: 240px;
    }

    .ant-popover-inner-content {
      padding: 0;
    }
  }

  .tsp-inner {
    min-width: 220px;
  }

  .tsp-section {
    padding: 12px 14px;
    border-bottom: 1px solid var(--line);

    &:last-child {
      border-bottom: 0;
    }
  }

  .tsp-label {
    font-size: 12px;
    color: var(--ink-500);
    font-weight: 600;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;

    .anticon {
      font-size: 12px;
      color: var(--ink-400);
    }
  }

  .tsp-seg {
    display: flex;
    background: var(--surface-3);
    border-radius: 8px;
    padding: 3px;
    gap: 2px;

    button {
      flex: 1;
      border: 0;
      background: transparent;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 500;
      color: var(--ink-500);
      padding: 6px 8px;
      border-radius: 6px;
      cursor: pointer;
      transition: background-color 0.15s, color 0.15s, box-shadow 0.15s;

      &:hover {
        color: var(--ink-900);
      }

      &.active {
        background: var(--surface);
        color: var(--accent);
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
      }
    }
  }

  .tsp-col-control {
    margin-bottom: 4px;
  }

  .tsp-col-header {
    border-bottom: 1px solid var(--line);
    margin-bottom: 4px;
    padding-bottom: 6px !important;
  }

  .tsp-columns {
    display: flex;
    flex-direction: column;
    gap: 0;
    max-height: 220px;
    overflow-y: auto;

    .ant-checkbox-group {
      display: flex;
      flex-direction: column;
      width: 100%;
    }
  }

  .tsp-col-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 4px;
    border-radius: 6px;
    font-size: 13px;
    color: var(--ink-700);
    cursor: pointer;
    transition: background-color 0.15s;
    width: 100%;

    &:hover {
      background: var(--surface-2);
    }

    .ant-checkbox-wrapper {
      flex: 1;
    }
  }

  .tsp-drag-icon {
    color: var(--ink-400);
    cursor: move;
    font-size: 13px;
    flex-shrink: 0;
  }

  .tsp-foot {
    display: flex;
    gap: 4px;
    padding: 8px 0 0;
    border-top: 1px solid var(--line);
    margin-top: 6px;

    button {
      flex: 1;
      padding: 5px;
      background: transparent;
      border: 0;
      border-radius: 6px;
      color: var(--ink-700);
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      font-family: inherit;
      transition: background-color 0.15s;

      &:hover {
        background: var(--surface-3);
      }

      &.tsp-save {
        color: var(--accent);

        &:hover {
          background: var(--accent-50);
        }
      }
    }
  }

  .tsp-fullscreen-row {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .tsp-label {
      margin-bottom: 0;
    }
  }
</style>
