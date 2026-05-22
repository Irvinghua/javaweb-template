<template>
  <div v-if="getMenuFixed && !getIsMobile" :style="getHiddenDomStyle" v-show="showClassSideBarRef"></div>
  <Sider
    v-show="showClassSideBarRef"
    ref="sideRef"
    breakpoint="lg"
    collapsible
    :class="getSiderClass"
    :width="getMenuWidth"
    :collapsed="getCollapsed"
    :collapsedWidth="getCollapsedWidth"
    :theme="getMenuTheme"
    @breakpoint="onBreakpointChange"
    :trigger="getTrigger"
    v-bind="getTriggerAttr"
  >
    <template #trigger v-if="getShowTrigger">
      <LayoutTrigger />
    </template>
    <LayoutMenu :theme="getMenuTheme" :menuMode="getMode" :splitType="getSplitType" />
    <DragBar ref="dragBarRef" />
  </Sider>
</template>
<script lang="ts">
  import { computed, defineComponent, ref, unref, CSSProperties, h } from 'vue';

  import { Layout } from 'ant-design-vue';
  import LayoutMenu from '../menu/index.vue';
  import LayoutTrigger from '/@/layouts/default/trigger/index.vue';

  import { MenuModeEnum, MenuSplitTyeEnum } from '/@/enums/menuEnum';

  import { useAppStore } from "@/store/modules/app";
  import { useGlobSetting } from "/@/hooks/setting";
  import { useMenuSetting } from '/@/hooks/setting/useMenuSetting';
  import { useTrigger, useDragLine, useSiderEvent } from './useLayoutSider';
  import { useAppInject } from '/@/hooks/web/useAppInject';
  import { useDesign } from '/@/hooks/web/useDesign';

  import DragBar from './DragBar.vue';

  export default defineComponent({
    name: 'LayoutSideBar',
    components: { Sider: Layout.Sider, LayoutMenu, DragBar, LayoutTrigger },
    setup() {
      const dragBarRef = ref<ElRef>(null);
      const sideRef = ref<ElRef>(null);

      const { getCollapsed, getMenuWidth, getSplit, getMenuTheme, getRealWidth, getMenuHidden, getMenuFixed, getIsMixMode, toggleCollapsed } =
        useMenuSetting();

      const { prefixCls } = useDesign('layout-sideBar');

      const glob = useGlobSetting()
      const appStore = useAppStore()

      const { getIsMobile } = useAppInject();

      const { getTriggerAttr, getShowTrigger } = useTrigger(getIsMobile);

      useDragLine(sideRef, dragBarRef);

      const { getCollapsedWidth, onBreakpointChange } = useSiderEvent();

      const getMode = computed(() => {
        return unref(getSplit) ? MenuModeEnum.INLINE : null;
      });

      const getSplitType = computed(() => {
        return unref(getSplit) ? MenuSplitTyeEnum.LEFT : MenuSplitTyeEnum.NONE;
      });

      const showClassSideBarRef = computed(() => {
        // 控制是否显示侧边栏
        if (appStore.getLayoutHideSider) {
          return false;
        }
        return unref(getSplit) ? !unref(getMenuHidden) : true;
      });

      const getSiderClass = computed(() => {
        return [
          prefixCls,
          {
            [`${prefixCls}--fixed`]: unref(getMenuFixed),
            [`${prefixCls}--mix`]: unref(getIsMixMode) && !unref(getIsMobile),
            // 【JEECG作为乾坤子应用】
            [`${prefixCls}--qiankun-micro`]: glob.isQiankunMicro,
          },
        ];
      });

      const getHiddenDomStyle = computed((): CSSProperties => {
        const width = `${unref(getRealWidth)}px`;
        return {
          width: width,
          overflow: 'hidden',
          flex: `0 0 ${width}`,
          maxWidth: width,
          minWidth: width,
          transition: 'all 0.2s',
        };
      });

      // 在此处使用计算量可能会导致sider异常
      // andv 更新后，如果trigger插槽可用，则此处代码可废弃
      const getTrigger = h(LayoutTrigger);

      return {
        prefixCls,
        sideRef,
        dragBarRef,
        getIsMobile,
        getHiddenDomStyle,
        getSiderClass,
        getTrigger,
        getTriggerAttr,
        getCollapsedWidth,
        getMenuFixed,
        showClassSideBarRef,
        getMenuWidth,
        getCollapsed,
        getMenuTheme,
        onBreakpointChange,
        getMode,
        getSplitType,
        getShowTrigger,
        toggleCollapsed,
      };
    },
  });
</script>
<style lang="less">
  @prefix-cls: ~'@{namespace}-layout-sideBar';

  .@{prefix-cls} {
    z-index: @layout-sider-fixed-z-index;

    &--fixed {
      position: fixed !important;
      top: 0;
      left: 0;
      height: 100%;
    }

    // 【JEECG作为乾坤子应用】
    &--qiankun-micro {
      position: absolute !important;
    }

    &--mix {
      top: @header-height;
      height: calc(100% - @header-height);
    }

    // ---- Redesign: sidebar container ----
    // In sidebar nav mode (default), always use white surface regardless of
    // the theme class that may be set from cached user settings.
    // We target the fixed sidebar (not mix/mobile drawer).
    &--fixed,
    &:not(.ant-layout-sider-dark) {
      background-color: var(--surface) !important;
      border-right: 1px solid var(--line) !important;
      box-shadow: none !important;
      // Allow the active left-edge indicator (::before on menu items) to be visible
      overflow: visible !important;

      .ant-layout-sider-trigger {
        background-color: var(--surface) !important;
        color: var(--ink-500) !important;
        border-top: 1px solid var(--line);
        height: 40px;
        line-height: 40px;
        font-size: 14px;
        transition: background-color var(--fast), color var(--fast);

        &:hover {
          background-color: var(--surface-2) !important;
          color: var(--ink-900) !important;
        }

        .anticon {
          font-size: 16px;
        }
      }

      // The inner content area
      .ant-layout-sider-children {
        display: flex;
        flex-direction: column;
        // Keep clip for vertical scroll but allow left-edge overflow for active indicator
        overflow-x: visible;
        overflow-y: auto;
      }
    }

    // Dark theme only when NOT fixed sidebar (mix modes can keep dark if set)
    &.ant-layout-sider-dark:not(.@{prefix-cls}--fixed) {
      background-color: @sider-dark-bg-color;

      .ant-layout-sider-trigger {
        color: darken(@white, 25%);
        background-color: @trigger-dark-bg-color;

        &:hover {
          color: @white;
          background-color: @trigger-dark-hover-bg-color;
        }
      }
    }

    .ant-layout-sider-zero-width-trigger {
      top: 40%;
      z-index: 10;
    }

    & .ant-layout-sider-trigger {
      height: 40px;
      line-height: 40px;
    }
  }
</style>
