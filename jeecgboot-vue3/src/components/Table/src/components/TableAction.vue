<template>
  <div :class="[prefixCls, getAlign]" @click="onCellClick">
    <template v-for="(action, index) in getActions" :key="`${index}-${action.label}`">
      <template v-if="action.slot">
        <slot name="customButton"></slot>
      </template>
      <template v-else>
        <Tooltip v-if="action.tooltip" v-bind="getTooltip(action.tooltip)">
          <PopConfirmButton v-bind="action">
            <Icon :icon="action.icon" :class="{ 'mr-1': !!action.label }" v-if="action.icon" />
            <template v-if="action.label">{{ action.label }}</template>
          </PopConfirmButton>
        </Tooltip>
        <PopConfirmButton v-else v-bind="action">
          <Icon :icon="action.icon" :class="{ 'mr-1': !!action.label }" v-if="action.icon" />
          <template v-if="action.label">{{ action.label }}</template>
        </PopConfirmButton>
      </template>

      <Divider type="vertical" class="action-divider" v-if="divider && index < getActions.length - 1" />
    </template>
    <Dropdown
      :overlayClassName="dropdownCls"
      :trigger="['hover']"
      :dropMenuList="getDropdownList"
      popconfirm
      v-if="dropDownActions && getDropdownList.length > 0"
      :getPopupContainer="dropdownGetPopupContainer"
    >
      <slot name="more"></slot>
      <!--  设置插槽   -->
      <template v-slot:[item.slot] v-for="(item, index) in getDropdownSlotList" :key="`${index}-${item.label}`">
        <slot :name="item.slot"></slot>
      </template>

      <!-- ITEM 4: ⋯ more trigger — 28×28 ghost square -->
      <button class="row-btn more" v-if="!$slots.more" type="button">
        <svg viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg" width="14" height="14">
          <circle cx="3" cy="8" r="1.5"/>
          <circle cx="8" cy="8" r="1.5"/>
          <circle cx="13" cy="8" r="1.5"/>
        </svg>
      </button>
    </Dropdown>
  </div>
</template>
<script lang="ts">
  import { defineComponent, PropType, computed, toRaw, unref } from 'vue';
  import { MoreOutlined } from '@ant-design/icons-vue';
  import { Divider, Tooltip, TooltipProps } from 'ant-design-vue';
  import Icon from '/@/components/Icon/index';
  import { ActionItem, TableActionType } from '/@/components/Table';
  import { PopConfirmButton } from '/@/components/Button';
  import { Dropdown } from '/@/components/Dropdown';
  import { useDesign } from '/@/hooks/web/useDesign';
  import { useTableContext } from '../hooks/useTableContext';
  import { usePermission } from '/@/hooks/web/usePermission';
  import { isBoolean, isFunction, isString } from '/@/utils/is';
  import { propTypes } from '/@/utils/propTypes';
  import { ACTION_COLUMN_FLAG } from '../const';

  export default defineComponent({
    name: 'TableAction',
    components: { Icon, PopConfirmButton, Divider, Dropdown, MoreOutlined, Tooltip },
    props: {
      actions: {
        type: Array as PropType<ActionItem[]>,
        default: null,
      },
      dropDownActions: {
        type: Array as PropType<ActionItem[]>,
        default: null,
      },
      divider: propTypes.bool.def(true),
      outside: propTypes.bool,
      stopButtonPropagation: propTypes.bool.def(false),
    },
    setup(props) {
      const { prefixCls } = useDesign('basic-table-action');
      const dropdownCls = `${prefixCls}-dropdown`;
      let table: Partial<TableActionType> = {};

      const tempActionsAuth = {};
      const tempDropdownListAuth = {};

      if (!props.outside) {
        table = useTableContext();
      }

      const { hasPermission } = usePermission();
      function isIfShow(action: ActionItem): boolean {
        const ifShow = action.ifShow;

        let isIfShow = true;

        if (isBoolean(ifShow)) {
          isIfShow = ifShow;
        }
        if (isFunction(ifShow)) {
          isIfShow = ifShow(action);
        }
        return isIfShow;
      }

      // 共享层自动识别：label 含「删除 / delete」的操作自动按 danger 渲染（设计稿要求红色）
      function isDangerAction(action: ActionItem): boolean {
        if ((action as any).danger === true || (action as any).color === 'error') return true;
        const label = (action as any).label;
        if (!label || typeof label !== 'string') return false;
        return /删除|delete/i.test(label);
      }

      const getActions = computed(() => {
        return (toRaw(props.actions) || [])
          .filter((action) => {
            // -update-begin--author:liaozhiyang---date:20240619---for：【TV360X-528】列表配置了权限，在列表行上划过，都会执行hasPermission
            const auth: any = action.auth;
            let authResult;
            if (action.auth && typeof tempActionsAuth[auth] === 'boolean') {
              authResult = tempActionsAuth[auth];
            } else {
              authResult = hasPermission(action.auth);
              action.auth && (tempActionsAuth[auth] = authResult);
            }
            return authResult && isIfShow(action);
            // -update-end--author:liaozhiyang---date:20240619---for：【TV360X-528】列表配置了权限，在列表行上划过，都会执行hasPermission
          })
          .map((action) => {
            const { popConfirm } = action;
            // 代码逻辑说明: 【issues/951】table删除记录时按钮显示错位
            if (popConfirm) {
              const overlayClassName = popConfirm.overlayClassName;
              popConfirm.overlayClassName = `${overlayClassName ? overlayClassName : ''} ${prefixCls}-popconfirm`;
            }
            const danger = isDangerAction(action);
            return {
              getPopupContainer: () => unref((table as any)?.wrapRef.value) ?? document.body,
              type: 'link',
              size: 'small',
              ...action,
              ...(popConfirm || {}),
              // 代码逻辑说明: 【issues/936】表格操作栏删除当接口失败时，气泡确认框不会消失
              onConfirm: handelConfirm(popConfirm?.confirm),
              onCancel: popConfirm?.cancel,
              enable: !!popConfirm,
              danger,
              color: danger ? 'error' : (action as any).color,
            };
          });
      });

      const getDropdownList = computed((): any[] => {
        //过滤掉隐藏的dropdown,避免出现多余的分割线
        const list = (toRaw(props.dropDownActions) || []).filter((action) => {
          // -update-begin--author:liaozhiyang---date:20240619---for：【TV360X-528】列表配置了权限，在列表行上划过，都会执行hasPermission
          const auth: any = action.auth;
          let authResult;
          if (action.auth && typeof tempDropdownListAuth[auth] === 'boolean') {
            authResult = tempDropdownListAuth[auth];
          } else {
            authResult = hasPermission(action.auth);
            action.auth && (tempDropdownListAuth[auth] = authResult);
          }
          return authResult && isIfShow(action);
          // -update-end--author:liaozhiyang---date:20240619---for：【TV360X-528】列表配置了权限，在列表行上划过，都会执行hasPermission
        });
        return list.map((action, index) => {
          const { label, popConfirm } = action;
          // 代码逻辑说明: 【issues/951】table删除记录时按钮显示错位
          if (popConfirm) {
            const overlayClassName = popConfirm.overlayClassName;
            popConfirm.overlayClassName = `${overlayClassName ? overlayClassName : ''} ${prefixCls}-popconfirm`;
            // 代码逻辑说明: 【issues/7028】表格全屏后操作列中的下拉菜单和气泡确认框不显示
            if (!popConfirm.getPopupContainer) {
              popConfirm.getPopupContainer = () => {
                return (table as any)?.wrapRef?.value ?? document.body;
              };
            }
          }
          // 代码逻辑说明: 【issues/936】表格操作栏删除当接口失败时，气泡确认框不会消失
          if (popConfirm) {
            popConfirm.confirm = handelConfirm(popConfirm?.confirm);
          }
          const danger = isDangerAction(action);
          return {
            ...action,
            ...popConfirm,
            onConfirm: handelConfirm(popConfirm?.confirm),
            onCancel: popConfirm?.cancel,
            text: label,
            divider: index < list.length - 1 ? props.divider : false,
            danger,
            color: danger ? 'error' : (action as any).color,
          };
        });
      });
      /*
      2023-01-08
      liaozhiyang
      给传进来的函数包一层promise
      */
      const handelConfirm = (fn) => {
        if (typeof fn !== 'function') return fn;
        const anyc = () => {
          return new Promise<void>((resolve) => {
            const result = fn();
            if (Object.prototype.toString.call(result) === '[object Promise]') {
              result
                .finally(() => {
                  resolve();
                })
                .catch((err) => {
                  console.log(err);
                });
            } else {
              resolve();
            }
          });
        };
        return anyc;
      };
      const getDropdownSlotList = computed((): any[] => {
        return unref(getDropdownList).filter((item) => item.slot);
      });
      const getAlign = computed(() => {
        const columns = (table as TableActionType)?.getColumns?.() || [];
        const actionColumn = columns.find((item) => item.flag === ACTION_COLUMN_FLAG);
        return actionColumn?.align ?? 'left';
      });

      function getTooltip(data: string | TooltipProps): TooltipProps {
        return {
          getPopupContainer: () => unref((table as any)?.wrapRef.value) ?? document.body,
          placement: 'bottom',
          ...(isString(data) ? { title: data } : data),
        };
      }

      function onCellClick(e: MouseEvent) {
        if (!props.stopButtonPropagation) return;
        const path = e.composedPath() as HTMLElement[];
        const isInButton = path.find((ele) => {
          return ele.tagName?.toUpperCase() === 'BUTTON';
        });
        isInButton && e.stopPropagation();
      }
      // 代码逻辑说明: 【issues/7028】表格全屏后操作列中的下拉菜单和气泡确认框不显示
      const dropdownGetPopupContainer = () => {
        return (table as any)?.wrapRef?.value ?? document.body;
      };
      return { prefixCls, getActions, getDropdownList, getDropdownSlotList, getAlign, onCellClick, getTooltip, dropdownCls, dropdownGetPopupContainer };
    },
  });
</script>
<style lang="less">
  @prefix-cls: ~'@{namespace}-basic-table-action';

  .@{prefix-cls} {
    // ITEM 4: row-actions-v2 layout
    display: inline-flex;
    align-items: center;
    gap: 4px;

    &.left {
      justify-content: flex-start;
    }

    &.center {
      justify-content: center;
    }

    &.right {
      justify-content: flex-end;
    }

    // ITEM 4: 可见行操作 — .row-btn ghost style (替代原 link-action)
    button.ant-btn-link,
    button.ant-btn {
      height: 28px !important;
      padding: 0 10px !important;
      background: transparent !important;
      border: 1px solid var(--line) !important;
      border-radius: 6px !important;
      color: var(--ink-700) !important;
      font-size: 12.5px !important;
      font-weight: 500 !important;
      cursor: pointer;
      display: inline-flex !important;
      align-items: center !important;
      gap: 4px !important;
      transition: background-color 0.15s, color 0.15s, border-color 0.15s !important;
      box-shadow: none !important;
      white-space: nowrap;

      span:not(.anticon) {
        margin-left: 0 !important;
        line-height: 1 !important;
      }

      .anticon {
        font-size: 12px !important;
        margin: 0 !important;
      }

      &:hover {
        background: var(--accent-50) !important;
        color: var(--accent) !important;
        border-color: rgba(91, 108, 255, 0.3) !important;
      }

      // 危险操作 (删除等)
      &.ant-btn-dangerous {
        color: var(--bad) !important;
        border-color: var(--line) !important;

        &:hover {
          background: var(--bad-bg) !important;
          color: var(--bad) !important;
          border-color: var(--bad) !important;
        }
      }
    }

    // ⋯ more 按钮 — 28×28 square ghost
    .row-btn.more {
      width: 28px !important;
      height: 28px !important;
      padding: 0 !important;
      background: transparent;
      border: 1px solid var(--line);
      border-radius: 6px;
      color: var(--ink-700);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: background-color 0.15s, color 0.15s, border-color 0.15s;

      svg {
        width: 14px;
        height: 14px;
        display: block;
      }

      &:hover {
        background: var(--accent-50);
        color: var(--accent);
        border-color: rgba(91, 108, 255, 0.3);
      }
    }

    // 隐藏 divider — gap 已足够
    .ant-divider,
    .ant-divider-vertical {
      display: none !important;
    }

    &-popconfirm {
      .ant-popconfirm-buttons {
        min-width: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
    }

    // ITEM 4: 下拉菜单 — .menu-pop 风格
    &-dropdown {
      .ant-dropdown-menu {
        background: var(--surface) !important;
        border: 1px solid var(--line) !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 28px rgba(15, 23, 42, 0.16) !important;
        padding: 5px !important;
        min-width: 128px;
      }

      .ant-dropdown-menu .ant-dropdown-menu-item-divider {
        height: 1px;
        background: var(--line) !important;
        margin: 4px 6px !important;
      }

      .ant-dropdown-menu .ant-dropdown-menu-item {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        padding: 8px 10px !important;
        font-size: 13px !important;
        color: var(--ink-700) !important;
        border-radius: 7px !important;
        transition: background-color 0.15s !important;

        &:hover {
          background: var(--surface-2) !important;
          color: var(--ink-700) !important;
        }

        // icon color
        .anticon {
          width: 14px;
          height: 14px;
          color: var(--ink-400);
          font-size: 13px !important;
        }

        &.ant-dropdown-menu-item-danger {
          color: var(--bad) !important;

          .anticon {
            color: var(--bad) !important;
          }

          &:hover {
            background: var(--bad-bg) !important;
            color: var(--bad) !important;
          }
        }
      }

      .dropdown-event-area {
        padding: 0 !important;
      }
    }
  }
</style>
