<template>
  <div :class="getWrapClass" @click="closeCtxMenu">
    <!-- Sidebar collapse toggle — leftmost of the tabs row -->
    <button class="tabs-row-trigger icon-btn" :aria-label="getCollapsed ? '展开侧边栏' : '收起侧边栏'" @click.stop="toggleCollapsed">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="6" x2="21" y2="6"/>
        <line x1="3" y1="12" x2="15" y2="12"/>
        <line x1="3" y1="18" x2="21" y2="18"/>
      </svg>
    </button>

    <!-- Custom pill capsule tabs — faithful mockup match -->
    <div class="tabs-capsule" role="tablist">
      <template v-for="item in getTabsState" :key="item.query ? item.fullPath : item.path">
        <button
          class="tab-pill"
          :class="{ active: activeKeyRef === (item.query ? item.fullPath : item.path) }"
          role="tab"
          :aria-selected="activeKeyRef === (item.query ? item.fullPath : item.path)"
          @click.stop="handleChange(item.query ? item.fullPath : item.path)"
          @contextmenu.prevent="(e) => openCtxMenu(e, item)"
        >
          <span class="tab-dot"></span>
          <TabContent :tabItem="item" />
          <span
            v-if="!(item && item.meta && item.meta.affix)"
            class="tab-close"
            :title="t('common.closeText')"
            @click.stop="handleEdit(item.query ? item.fullPath : item.path)"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="10" height="10">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </span>
        </button>
      </template>
    </div>

    <!-- Tab right-click context menu -->
    <Teleport to="body">
      <div
        v-if="ctxMenu.visible"
        class="tab-ctx"
        :style="{ left: ctxMenu.x + 'px', top: ctxMenu.y + 'px' }"
        @click.stop
      >
        <!-- 刷新当前 -->
        <button @click="ctxAction('refresh')" :disabled="!ctxMenu.isCurrentTab">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          刷新当前
        </button>
        <!-- 关闭当前 -->
        <button @click="ctxAction('close')" :disabled="!!ctxMenu.tab?.meta?.affix">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          关闭当前
        </button>
        <!-- 关闭其他 -->
        <button @click="ctxAction('closeOther')" :disabled="getTabsState.length <= 1">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>
          关闭其他
        </button>
        <!-- 关闭右侧 -->
        <button @click="ctxAction('closeRight')" :disabled="ctxMenu.isLast">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
          关闭右侧
        </button>
        <!-- 关闭全部 -->
        <button @click="ctxAction('closeAll')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
          关闭全部
        </button>
      </div>
    </Teleport>
  </div>
</template>
<script lang="ts">
  import type { RouteLocationNormalized, RouteMeta } from 'vue-router';

  import { defineComponent, computed, unref, ref, reactive, onMounted, onUnmounted } from 'vue';

  import TabContent from './components/TabContent.vue';
  import FoldButton from './components/FoldButton.vue';
  import TabRedo from './components/TabRedo.vue';

  import { useGo } from '/@/hooks/web/usePage';
  import { useTabs } from '/@/hooks/web/useTabs';

  import { useMultipleTabStore } from '/@/store/modules/multipleTab';
  import { useUserStore } from '/@/store/modules/user';

  import { initAffixTabs, useTabsDrag } from './useMultipleTabs';
  import { useDesign } from '/@/hooks/web/useDesign';
  import { useMultipleTabSetting } from '/@/hooks/setting/useMultipleTabSetting';
  import { useMenuSetting } from '/@/hooks/setting/useMenuSetting';
  import { useI18n } from '/@/hooks/web/useI18n';

  import { REDIRECT_NAME } from '/@/router/constant';
  import { listenerRouteChange } from '/@/logics/mitt/routeChange';

  import { useRouter } from 'vue-router';

  export default defineComponent({
    name: 'MultipleTabs',
    components: {
      TabRedo,
      FoldButton,
      TabContent,
    },
    setup() {
      const affixTextList = initAffixTabs();
      const activeKeyRef = ref('');
      const { t } = useI18n();

      useTabsDrag(affixTextList);
      const tabStore = useMultipleTabStore();
      const userStore = useUserStore();
      const router = useRouter();
      const { getCollapsed, toggleCollapsed } = useMenuSetting();

      const { prefixCls } = useDesign('multiple-tabs');
      const go = useGo();
      const { getShowQuick, getShowRedo, getShowFold, getTabsTheme } = useMultipleTabSetting();
      const { refreshPage, close, closeAll, closeLeft, closeRight, closeOther } = useTabs(router);

      const getTabsState = computed(() => {
        return tabStore.getTabList.filter((item) => !item.meta?.hideTab);
      });

      const unClose = computed(() => unref(getTabsState).length === 1);

      const getWrapClass = computed(() => {
        return [
          prefixCls,
          {
            [`${prefixCls}--hide-close`]: unref(unClose),
          },
          `${prefixCls}--theme-${unref(getTabsTheme)}`,
        ];
      });

      listenerRouteChange((route) => {
        const { name } = route;
        if (name === REDIRECT_NAME || !route || !userStore.getToken) {
          return;
        }

        const { path, fullPath, meta = {} } = route;
        const { currentActiveMenu, hideTab } = meta as RouteMeta;
        const isHide = !hideTab ? null : currentActiveMenu;
        const p = isHide || fullPath || path;
        if (activeKeyRef.value !== p) {
          activeKeyRef.value = p as string;
        }

        if (isHide) {
          const findParentRoute = router.getRoutes().find((item) => item.path === currentActiveMenu);

          findParentRoute && tabStore.addTab(findParentRoute as unknown as RouteLocationNormalized);
        } else {
          tabStore.addTab(unref(route));
        }
      });

      function handleChange(activeKey: any) {
        activeKeyRef.value = activeKey;
        go(activeKey, false);
      }

      // Close the current tab
      function handleEdit(targetKey: string) {
        // Added operation to hide, currently only use delete operation
        if (unref(unClose)) {
          return;
        }

        tabStore.closeTabByKey(targetKey, router);
      }

      // ---- Context menu ----
      const ctxMenu = reactive({
        visible: false,
        x: 0,
        y: 0,
        tab: null as RouteLocationNormalized | null,
        isCurrentTab: false,
        isLast: false,
      });

      function openCtxMenu(e: MouseEvent, tab: RouteLocationNormalized) {
        const tabList = unref(getTabsState);
        const idx = tabList.findIndex((t) => t.path === tab.path);
        ctxMenu.tab = tab;

        const menuWidth = 170;
        const menuHeight = 185; // approx height for 5 items

        // X position — clamp to viewport right edge
        let x = e.clientX;
        if (x + menuWidth > window.innerWidth) {
          x = window.innerWidth - menuWidth - 8;
        }
        ctxMenu.x = x;

        // Y position — position below click. Clamp so menu never hides under header.
        let y = e.clientY + 8;
        // If too close to bottom, try above click point
        if (y + menuHeight > window.innerHeight) {
          y = e.clientY - menuHeight - 4;
        }
        // Never go above viewport or under the header (header ~88px)
        const minY = 94;
        if (y < minY) y = minY;
        ctxMenu.y = y;

        ctxMenu.isCurrentTab = tab.path === unref(router.currentRoute).path;
        ctxMenu.isLast = idx === tabList.length - 1;
        ctxMenu.visible = true;
      }

      function closeCtxMenu() {
        ctxMenu.visible = false;
      }

      async function ctxAction(action: string) {
        const tab = ctxMenu.tab as RouteLocationNormalized;
        closeCtxMenu();
        switch (action) {
          case 'refresh':
            await refreshPage();
            break;
          case 'close':
            if (!tab?.meta?.affix) {
              await close(tab);
            }
            break;
          case 'closeOther':
            await closeOther(tab);
            break;
          case 'closeRight':
            await closeRight(tab);
            break;
          case 'closeAll':
            await closeAll(tab);
            break;
        }
      }

      // Close context menu on global click / Escape
      function onDocClick() { ctxMenu.visible = false; }
      function onEsc(e: KeyboardEvent) { if (e.key === 'Escape') ctxMenu.visible = false; }
      onMounted(() => {
        document.addEventListener('click', onDocClick);
        document.addEventListener('keydown', onEsc);
      });
      onUnmounted(() => {
        document.removeEventListener('click', onDocClick);
        document.removeEventListener('keydown', onEsc);
      });

      return {
        prefixCls,
        unClose,
        getWrapClass,
        handleEdit,
        handleChange,
        activeKeyRef,
        getTabsState,
        getShowQuick,
        getShowRedo,
        getShowFold,
        getCollapsed,
        toggleCollapsed,
        t,
        ctxMenu,
        openCtxMenu,
        closeCtxMenu,
        ctxAction,
      };
    },
  });
</script>
<style lang="less">
  @import './index.less';

  // Tab right-click context menu (rendered via Teleport to body)
  .tab-ctx {
    position: fixed;
    z-index: 300;
    min-width: 160px;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 10px;
    box-shadow: var(--shadow-pop);
    padding: 4px;

    button {
      display: flex;
      align-items: center;
      gap: 8px;
      width: 100%;
      padding: 7px 10px;
      background: transparent;
      border: 0;
      border-radius: 6px;
      font-size: 12.5px;
      color: var(--ink-700);
      cursor: pointer;
      text-align: left;
      font-family: inherit;
      transition: background-color var(--fast), color var(--fast);

      &:hover {
        background: var(--surface-2);
        color: var(--ink-900);
      }

      &:disabled {
        opacity: 0.45;
        cursor: not-allowed;
        pointer-events: none;
      }

      svg {
        width: 13px;
        height: 13px;
        color: var(--ink-500);
        flex-shrink: 0;
      }
    }
  }
</style>
<style lang="less" scoped>
@prefix-cls: ~'@{namespace}-multiple-tabs';
.@{prefix-cls} {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1 1 0;
  min-width: 0;

  .tabs-row-trigger.icon-btn {
    width: 36px;
    height: 36px;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
    display: grid;
    place-items: center;
    cursor: pointer;
    color: var(--ink-600);
    flex-shrink: 0;
    transition: background-color var(--fast), color var(--fast);

    svg {
      width: 17px;
      height: 17px;
    }

    &:hover {
      background: var(--surface-2);
      color: var(--ink-900);
    }
  }

  // Capsule tab strip
  .tabs-capsule {
    flex: 1 1 0;
    display: flex;
    gap: 2px;
    min-width: 0;
    overflow-x: auto;
    scrollbar-width: none;
    padding: 3px;
    background: var(--surface-2);
    border-radius: 10px;
    border: 1px solid var(--line);

    &::-webkit-scrollbar {
      display: none;
    }
  }

  .tab-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 10px 6px 8px;
    border-radius: 7px;
    background: transparent;
    border: 0;
    font-size: 12.5px;
    color: var(--ink-600);
    font-weight: 500;
    cursor: pointer;
    white-space: nowrap;
    transition: background-color var(--fast), color var(--fast);
    user-select: none;
    font-family: inherit;
    flex-shrink: 0;

    &:hover {
      background: var(--surface);
      color: var(--ink-900);

      .tab-close {
        opacity: 1;
      }
    }

    &.active {
      background: var(--surface);
      color: var(--accent);
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
      font-weight: 600;

      .tab-dot {
        background: var(--accent);
      }

      .tab-close {
        opacity: 1;
      }
    }
  }

  .tab-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--ink-300);
    flex-shrink: 0;
  }

  .tab-close {
    margin-left: 2px;
    width: 16px;
    height: 16px;
    border-radius: 5px;
    color: var(--ink-400);
    opacity: 0.55;
    display: inline-grid;
    place-items: center;
    transition: background-color var(--fast), color var(--fast), opacity var(--fast);
    flex-shrink: 0;

    &:hover {
      background: var(--line-strong);
      color: var(--ink-700);
      opacity: 1;
    }
  }

  // Hide close when only one tab
  &--hide-close .tab-close {
    opacity: 0 !important;
    pointer-events: none;
  }
}
</style>
