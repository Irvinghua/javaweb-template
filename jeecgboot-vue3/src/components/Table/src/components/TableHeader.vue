<template>
  <div style="width: 100%">
    <div v-if="$slots.headerTop" style="margin: 5px">
      <slot name="headerTop"></slot>
    </div>
    <div :class="`${prefixCls}__table-title-box`">
      <div :class="`${prefixCls}__tableTitle`">
        <slot name="tableTitle" v-if="$slots.tableTitle"></slot>
        <!--修改标题插槽位置-->
        <TableTitle :helpMessage="titleHelpMessage" :title="title" v-if="!$slots.tableTitle && title" />
      </div>

      <div :class="`${prefixCls}__toolbar`">
        <slot name="toolbar"></slot>
        <Divider type="vertical" v-if="$slots.toolbar && showTableSetting" />
        <TableSetting :class="`${prefixCls}__toolbar-desktop`" style="white-space: nowrap;" :setting="tableSetting" v-if="showTableSetting" @columns-change="handleColumnChange" />
      </div>
    </div>
    <!--添加tableTop插槽-->
    <div class="basic-table-header__alert-wrap" v-if="openRowSelection != null || $slots.tableTop">
      <slot name="tableTop">
        <div class="basic-table-alert-info" v-if="openRowSelection != null">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="basic-table-alert-icon"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          <template v-if="selectRowKeys.length > 0">
            已选中 <b>{{ selectRowKeys.length }}</b> 条记录
            <span v-if="isAcrossPage">（可跨页）</span>
            <a-divider type="vertical" />
            <a class="basic-table-alert-clear" @click="setSelectedRowKeys([])">清空</a>
            <slot name="alertAfter" />
          </template>
          <template v-else>
            未选中任何数据
          </template>
        </div>
      </slot>
    </div>
    <!--添加tableTop插槽-->
  </div>
</template>
<script lang="ts">
  import type { TableSetting, ColumnChangeParam } from '../types/table';
  import type { PropType } from 'vue';
  import { defineComponent, computed } from 'vue';
  import { Divider } from 'ant-design-vue';
  import TableSettingComponent from './settings/index.vue';
  import TableTitle from './TableTitle.vue';
  import { useDesign } from '/@/hooks/web/useDesign';
  import { useTableContext } from '../hooks/useTableContext';

  export default defineComponent({
    name: 'BasicTableHeader',
    components: {
      Divider,
      TableTitle,
      TableSetting: TableSettingComponent,
    },
    props: {
      title: {
        type: [Function, String] as PropType<string | ((data: Recordable) => string)>,
      },
      tableSetting: {
        type: Object as PropType<TableSetting>,
      },
      showTableSetting: {
        type: Boolean,
      },
      titleHelpMessage: {
        type: [String, Array] as PropType<string | string[]>,
        default: '',
      },
    },
    emits: ['columns-change'],
    setup(_, { emit }) {
      const { prefixCls } = useDesign('basic-table-header');

      function handleColumnChange(data: ColumnChangeParam[]) {
        emit('columns-change', data);
      }

      const { getSelectRowKeys, setSelectedRowKeys, getRowSelection } = useTableContext();
      const selectRowKeys = computed(() => getSelectRowKeys());
      const openRowSelection = computed(() => getRowSelection());
      // 是否允许跨页选择
      const isAcrossPage = computed(() => openRowSelection.value?.preserveSelectedRowKeys === true);

      return { prefixCls, handleColumnChange, selectRowKeys, setSelectedRowKeys, openRowSelection, isAcrossPage };
    },
  });
</script>
<style lang="less">
  @prefix-cls: ~'@{namespace}-basic-table-header';

  .@{prefix-cls} {
    &__table-title-box {
      display: flex;
      align-items: center;
      width: 100%;
    }

    &__toolbar {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 8px;
      margin-left: auto;
      flex-shrink: 0;

      &-desktop {
        display: flex;
      }

      &-mobile {
        display: none;
      }
    }

    &__tableTitle {
      flex: 1;
      display: flex;
      flex-wrap: wrap;
      align-content: flex-start;

      > * {
        margin-right: 4px;
        margin-bottom: 4px;
      }
    }

    &__alert-wrap {
      // UI Redesign: 占位（实际 DOM class 是不带前缀的 .basic-table-header__alert-wrap，
      // 真正生效的规则见下方）
      margin-top: 14px;
    }

    @media (max-width: @screen-lg) {
      &__table-title-box {
        align-items: flex-end;
      }

      &__toolbar {
        &-desktop {
          display: none;
        }

        &-mobile {
          display: flex;
        }
      }
    }
  }

  // ⚠️ 注意：template 里 .basic-table-header__alert-wrap 是不带 @prefix-cls 前缀的字面量类名，
  // 不能写成 `.@{prefix-cls}__alert-wrap`（那会编译成 .jeecg-basic-table-header__alert-wrap）。
  // 这里独立挂一条规则，确保按钮行 → alert 行有 14px 间距。
  .basic-table-header__alert-wrap {
    margin-top: 14px;
  }

  /* 已选提示条 */
  .basic-table-alert-info {
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--accent-50);
    border: 1px solid rgba(91, 108, 255, 0.14);
    color: var(--ink-700);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;

    b {
      color: var(--accent-600);
      font-weight: 600;
    }
  }

  .basic-table-alert-icon {
    width: 15px;
    height: 15px;
    color: var(--accent);
    flex-shrink: 0;
  }

  .basic-table-alert-clear {
    color: var(--accent);
    cursor: pointer;

    &:hover {
      text-decoration: underline;
    }
  }
</style>
