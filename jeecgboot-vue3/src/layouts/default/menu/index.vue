<script lang="tsx">
  import type { PropType, CSSProperties } from 'vue';

  import { computed, defineComponent, unref, toRef } from 'vue';
  import { BasicMenu } from '/@/components/Menu';
  import { SimpleMenu } from '/@/components/SimpleMenu';
  import { AppLogo } from '/@/components/Application';

  import { MenuModeEnum, MenuSplitTyeEnum } from '/@/enums/menuEnum';

  import { useMenuSetting } from '/@/hooks/setting/useMenuSetting';
  import { ScrollContainer } from '/@/components/Container';

  import { useGo } from '/@/hooks/web/usePage';
  import { useGlobSetting } from "/@/hooks/setting";
  import { useSplitMenu } from './useLayoutMenu';
  import { openWindow } from '/@/utils';
  import { propTypes } from '/@/utils/propTypes';
  import { isUrl } from '/@/utils/is';
  import { useRootSetting } from '/@/hooks/setting/useRootSetting';
  import { useAppInject } from '/@/hooks/web/useAppInject';
  import { useDesign } from '/@/hooks/web/useDesign';
  import { useLocaleStore } from '/@/store/modules/locale';

  export default defineComponent({
    name: 'LayoutMenu',
    props: {
      theme: propTypes.oneOf(['light', 'dark']),

      splitType: {
        type: Number as PropType<MenuSplitTyeEnum>,
        default: MenuSplitTyeEnum.NONE,
      },

      isHorizontal: propTypes.bool,
      // menu Mode
      menuMode: {
        type: [String] as PropType<Nullable<MenuModeEnum>>,
        default: '',
      },
    },
    setup(props) {
      const go = useGo();

      const {
        getMenuMode,
        getMenuType,
        getMenuTheme,
        getCollapsed,
        getCollapsedShowTitle,
        getAccordion,
        getIsHorizontal,
        getIsSidebarType,
        getSplit,
      } = useMenuSetting();

      // expose getCollapsed for renderMenu to use
      const collapsedRef = getCollapsed;
      const { getShowLogo } = useRootSetting();

      const { prefixCls } = useDesign('layout-menu');

      const glob = useGlobSetting()

      const { menusRef } = useSplitMenu(toRef(props, 'splitType'));

      const { getIsMobile } = useAppInject();

      const getComputedMenuMode = computed(() => (unref(getIsMobile) ? MenuModeEnum.INLINE : props.menuMode || unref(getMenuMode)));

      const getComputedMenuTheme = computed(() => props.theme || unref(getMenuTheme));

      const getIsShowLogo = computed(() => unref(getShowLogo) && unref(getIsSidebarType));

      const getUseScroll = computed(() => {
        // 【JEECG作为乾坤子应用】在乾坤子应用下，菜单不固定
        if (glob.isQiankunMicro) {
          return false;
        }

        return (
          !unref(getIsHorizontal) &&
          (unref(getIsSidebarType) || props.splitType === MenuSplitTyeEnum.LEFT || props.splitType === MenuSplitTyeEnum.NONE)
        );
      });

      const getWrapperStyle = computed((): CSSProperties => {
        return {
          // 代码逻辑说明: 【issues/7548】侧边栏导航模式时会导致下面菜单滚动显示不全
          height: `calc(100% - ${unref(getIsShowLogo) ? '60px' : '0px'})`,
        };
      });

      const getLogoClass = computed(() => {
        return [
          `${prefixCls}-logo`,
          unref(getComputedMenuTheme),
          {
            [`${prefixCls}--mobile`]: unref(getIsMobile),
          },
        ];
      });

      const getCommonProps = computed(() => {
        const menus = unref(menusRef);
        return {
          menus,
          beforeClickFn: beforeMenuClickFn,
          items: menus,
          theme: unref(getComputedMenuTheme),
          accordion: unref(getAccordion),
          collapse: unref(getCollapsed),
          collapsedShowTitle: unref(getCollapsedShowTitle),
          onMenuClick: handleMenuClick,
        };
      });
      /**
       * click menu
       * @param menu
       */
      // 代码逻辑说明: VUEN-1144 online 配置成菜单后，打开菜单，显示名称未展示为菜单名称
      const localeStore = useLocaleStore();
      function handleMenuClick(path: string, item) {
        if (item) {
          localeStore.setPathTitle(path, item.title || '');
        }
        go(path);
      }

      /**
       * before click menu
       * @param menu
       */
      async function beforeMenuClickFn(path: string) {
        if (!isUrl(path)) {
          return true;
        }
        openWindow(path);
        return false;
      }

      function renderHeader() {
        if (!unref(getIsShowLogo) && !unref(getIsMobile)) return null;

        return <AppLogo showTitle={!unref(getCollapsed)} class={unref(getLogoClass)} theme={unref(getComputedMenuTheme)} />;
      }

      // Paths that belong to 系统设置 group
      const SETTINGS_PATHS = ['/isystem', '/mytenant', '/monitor', '/message'];

      function renderMenu() {
        const { menus, ...menuProps } = unref(getCommonProps);
        // console.log(menus);
        if (!menus || !menus.length) return null;

        if (props.isHorizontal) {
          return (
            <BasicMenu
              {...(menuProps as any)}
              isHorizontal={props.isHorizontal}
              type={unref(getMenuType)}
              showLogo={unref(getIsShowLogo)}
              mode={unref(getComputedMenuMode as any)}
              items={menus}
            />
          );
        }

        // Vertical sidebar — split into main/settings groups
        const isCollapsed = unref(getCollapsed);
        const mainMenus = menus.filter((item) => !SETTINGS_PATHS.includes(item.path));
        const settingsMenus = menus.filter((item) => SETTINGS_PATHS.includes(item.path));

        const groupTitle = (title: string) =>
          !isCollapsed ? <div class="nav-group-title">{title}</div> : null;

        return (
          <div class="sidebar-menu-groups">
            {mainMenus.length > 0 && (
              <div class="nav-section">
                {groupTitle('主菜单')}
                <SimpleMenu {...menuProps} isSplitMenu={unref(getSplit)} items={mainMenus} />
              </div>
            )}
            {settingsMenus.length > 0 && (
              <div class="nav-section nav-section--settings">
                {groupTitle('系统设置')}
                <SimpleMenu {...menuProps} isSplitMenu={unref(getSplit)} items={settingsMenus} />
              </div>
            )}
          </div>
        );
      }

      return () => {
        return (
          <>
            {renderHeader()}
            {unref(getUseScroll) ? <ScrollContainer style={unref(getWrapperStyle)}>{() => renderMenu()}</ScrollContainer> : renderMenu()}
          </>
        );
      };
    },
  });
</script>
<style lang="less" scoped>
  // 代码逻辑说明: 【QQYUN-5872】菜单优化，上下滚动条去掉
  .scroll-container :deep(.scrollbar__bar) {
    display: none;
  }
</style>
<style lang="less">
  // Sidebar group headers and section layout
  .sidebar-menu-groups {
    display: flex;
    flex-direction: column;
    width: 100%;
  }

  .nav-section {
    display: flex;
    flex-direction: column;

    &--settings {
      margin-top: 14px;
      padding-top: 6px;
      border-top: 1px solid var(--line);
    }
  }

  .nav-group-title {
    font-size: 11px;
    font-weight: 700;
    color: var(--ink-400);
    text-transform: uppercase;
    letter-spacing: 1.2px;
    padding: 14px 14px 8px;
    line-height: 1;
    white-space: nowrap;
    overflow: hidden;
  }
</style>
<style lang="less">
  @prefix-cls: ~'@{namespace}-layout-menu';
  @logo-prefix-cls: ~'@{namespace}-app-logo';
  @menu-prefix-cls: ~'@{namespace}-menu';

  .@{prefix-cls} {
    &-logo {
      height: @header-height;
      padding: 10px 4px 10px 10px;

      img {
        width: @logo-width;
        height: @logo-width;
      }
    }

    &--mobile {
      .@{logo-prefix-cls} {
        &__title {
          opacity: 1;
        }
      }
    }
  }

  // Redesign override: when app-logo renders in dark mode inside fixed sidebar,
  // force light colors so it's always readable on white background.
  .jeecg-layout-sideBar--fixed .jeecg-app-logo {
    background: var(--surface) !important;

    &.dark .jeecg-app-logo__title {
      color: var(--ink-900) !important;
      font-weight: 700;
    }
  }

  // Redesign override: when sidebar menu uses dark class (from cached user settings),
  // force light redesign colors so sidebar always looks like the design spec.
  // This only applies inside the sidebar sider container (fixed layout sider).
  .jeecg-layout-sideBar--fixed {
    .@{menu-prefix-cls}-dark.@{menu-prefix-cls}-vertical {
      background-color: var(--surface) !important;

      // submenu parent container
      .jeecg-simple-menu__parent,
      .@{menu-prefix-cls}-submenu,
      .@{menu-prefix-cls}-submenu-nested {
        background-color: var(--surface) !important;
      }

      .@{menu-prefix-cls}-item,
      .@{menu-prefix-cls}-submenu-title {
        color: var(--ink-700) !important;

        &:hover {
          background-color: var(--surface-2) !important;
          color: var(--ink-900) !important;
        }
      }

      // Active leaf item (top-level)
      > .@{menu-prefix-cls}-item-active:not(.@{menu-prefix-cls}-submenu) {
        background-color: var(--accent-50) !important;
        color: var(--accent) !important;
        font-weight: 600;
        position: relative;

        &::before {
          content: '' !important;
          position: absolute;
          left: -14px;
          top: 10px;
          bottom: 10px;
          width: 3px;
          border-radius: 0 3px 3px 0;
          background-color: var(--accent) !important;
        }

        &::after {
          display: none !important;
        }
      }

      // Parent with active child
      .@{menu-prefix-cls}-child-item-active > .@{menu-prefix-cls}-submenu-title,
      .@{menu-prefix-cls}-submenu-active > .@{menu-prefix-cls}-submenu-title,
      .@{menu-prefix-cls}-opened > .@{menu-prefix-cls}-submenu-title {
        background-color: var(--surface-2) !important;
        color: var(--ink-900) !important;
      }

      // Nested sub-items (children of submenu)
      .@{menu-prefix-cls}-submenu .@{menu-prefix-cls}-item,
      .@{menu-prefix-cls}-submenu-nested .@{menu-prefix-cls}-item {
        color: var(--ink-600) !important;

        &:hover {
          background-color: var(--surface-2) !important;
          color: var(--ink-900) !important;
        }

        &.@{menu-prefix-cls}-item-active {
          background-color: var(--accent-50) !important;
          color: var(--accent) !important;
          font-weight: 600;

          &::after {
            display: none !important;
          }
        }
      }

      // Collapsed state
      &.@{menu-prefix-cls}-collapse {
        background-color: var(--surface) !important;

        > .@{menu-prefix-cls}-item-active,
        > .@{menu-prefix-cls}-submenu-active {
          background-color: var(--accent-50) !important;
          position: relative;

          &::before {
            content: '' !important;
            position: absolute;
            left: -10px;
            top: 50%;
            transform: translateY(-50%);
            width: 3px;
            height: 20px;
            border-radius: 0 3px 3px 0;
            background-color: var(--accent) !important;
          }
        }
      }
    }
  }
</style>
