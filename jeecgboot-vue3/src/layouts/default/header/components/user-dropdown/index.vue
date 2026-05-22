<template>
  <Dropdown placement="bottomLeft" :overlayClassName="`${prefixCls}-dropdown-overlay`">
    <span :class="[prefixCls, `${prefixCls}--${theme}`]" class="flex">
      <img :class="`${prefixCls}__header`" :src="getAvatarUrl" />
      <span :class="`${prefixCls}__info hidden md:block`">
        <span :class="`${prefixCls}__name  `" class="truncate">
          {{ getUserInfo.realname }}
        </span>
      </span>
    </span>

    <template #overlay>
      <div :class="`${prefixCls}-pop-menu`">
        <!-- Header -->
        <div :class="`${prefixCls}-pop-menu__head`">
          <span>{{ getUserInfo.realname }}</span>
        </div>

        <!-- Menu items -->
        <button v-if="getShowDoc" :class="`${prefixCls}-pop-menu__item`" @click="handleMenuClick({ key: 'doc' })">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          {{ t('layout.header.dropdownItemDoc') }}
        </button>
        <div v-if="getShowDoc" :class="`${prefixCls}-pop-menu__sep`"></div>

        <button :class="`${prefixCls}-pop-menu__item`" @click="handleMenuClick({ key: 'account' })">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          {{ t('layout.header.dropdownItemSwitchAccount') }}
        </button>
        <button :class="`${prefixCls}-pop-menu__item`" @click="handleMenuClick({ key: 'password' })">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          {{ t('layout.header.dropdownItemSwitchPassword') }}
        </button>
        <button :class="`${prefixCls}-pop-menu__item`" @click="handleMenuClick({ key: 'depart' })">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          {{ t('layout.header.dropdownItemSwitchDepart') }}
        </button>
        <button :class="`${prefixCls}-pop-menu__item`" @click="handleMenuClick({ key: 'cache' })">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          {{ t('layout.header.dropdownItemRefreshCache') }}
        </button>

        <!-- Theme swatches -->
        <div :class="`${prefixCls}-pop-menu__sep`"></div>
        <div :class="`${prefixCls}-pop-menu__swatches`">
          <span
            v-for="color in themeColorList"
            :key="color"
            :class="[`${prefixCls}-pop-menu__swatch`, { active: currentThemeColor === color }]"
            :style="{ background: color }"
            :title="color"
            @click="handleThemeColor(color)"
          ></span>
        </div>
        <div :class="`${prefixCls}-pop-menu__sep`"></div>

        <!-- Logout -->
        <button :class="[`${prefixCls}-pop-menu__item`, `${prefixCls}-pop-menu__item--danger`]" @click="handleMenuClick({ key: 'logout' })">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          {{ t('layout.header.dropdownItemLoginOut') }}
        </button>
      </div>
    </template>
  </Dropdown>
  <LockAction v-if="lockActionVisible" ref="lockActionRef" @register="register" />
  <DepartSelect ref="loginSelectRef" />
  <UpdatePassword v-if="passwordVisible" ref="updatePasswordRef" />
</template>
<script lang="ts">
  // components
  import { Dropdown, Menu } from 'ant-design-vue';

  import { defineComponent, computed, ref, nextTick } from 'vue';

  import { SITE_URL } from '/@/settings/siteSetting';

  import { useUserStore } from '/@/store/modules/user';
  import { useHeaderSetting } from '/@/hooks/setting/useHeaderSetting';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { useDesign } from '/@/hooks/web/useDesign';
  import { useModal } from '/@/components/Modal';
  import { useMessage } from '/src/hooks/web/useMessage';
  import { useGo } from '/@/hooks/web/usePage';
  import headerImg from '/@/assets/images/header.jpg';
  import { propTypes } from '/@/utils/propTypes';
  import { openWindow } from '/@/utils';

  import { createAsyncComponent } from '/@/utils/factory/createAsyncComponent';

  import { refreshCache, queryAllDictItems } from '/@/views/system/dict/dict.api';
  import { DB_DICT_DATA_KEY } from '/src/enums/cacheEnum';
  import { removeAuthCache, setAuthCache } from '/src/utils/auth';
  import { getFileAccessHttpUrl } from '/@/utils/common/compUtils';
  import { getRefPromise } from '/@/utils/index';
  import { refreshDragCache } from "@/api/common/api";
  import { useAppStore } from '/@/store/modules/app';
  import { baseHandler } from '/@/layouts/default/setting/handler';
  import { HandlerEnum } from '/@/layouts/default/setting/enum';
  import { useRootSetting } from '/@/hooks/setting/useRootSetting';

  type MenuEvent = 'logout' | 'doc' | 'lock' | 'cache' | 'depart' | 'defaultHomePage' | 'password' | 'account';
  const { createMessage } = useMessage();
  export default defineComponent({
    name: 'UserDropdown',
    components: {
      Dropdown,
      Menu,
      MenuItem: createAsyncComponent(() => import('./DropMenuItem.vue')),
      MenuDivider: Menu.Divider,
      LockAction: createAsyncComponent(() => import('../lock/LockModal.vue')),
      DepartSelect: createAsyncComponent(() => import('./DepartSelect.vue')),
      UpdatePassword: createAsyncComponent(() => import('./UpdatePassword.vue')),
    },
    props: {
      theme: propTypes.oneOf(['dark', 'light']),
    },
    setup() {
      const { prefixCls } = useDesign('header-user-dropdown');
      const { t } = useI18n();
      const { getShowDoc, getUseLockPage } = useHeaderSetting();
      const userStore = useUserStore();
      const { getThemeColor } = useRootSetting();

      // Theme color presets — 6 个，与设计稿主题色板数量一致（首个为当前主色）
      const themeColorList = ['#5B6CFF', '#0EA5E9', '#10B981', '#8B5CF6', '#F59E0B', '#F43F5E'];

      const currentThemeColor = computed(() => getThemeColor.value);

      function handleThemeColor(color: string) {
        baseHandler(HandlerEnum.CHANGE_THEME_COLOR, color);
      }
      const go = useGo();
      const passwordVisible = ref(false);
      const lockActionVisible = ref(false);
      const lockActionRef = ref(null);

      const getUserInfo = computed(() => {
        const { realname = '', avatar, desc } = userStore.getUserInfo || {};
        return { realname, avatar: avatar || headerImg, desc };
      });

      const getAvatarUrl = computed(() => {
        let { avatar } = getUserInfo.value;
        if (avatar == headerImg) {
          return avatar;
        } else {
          return getFileAccessHttpUrl(avatar);
        }
      });

      const [register, { openModal }] = useModal();
      /**
       * 多部门弹窗逻辑
       */
      const loginSelectRef = ref();
      // 代码逻辑说明: 【QQYUN-6333】空路由问题—首次访问资源太大
      async function handleLock() {
        await getRefPromise(lockActionRef);
        openModal(true);
      }
      //  login out
      function handleLoginOut() {
        userStore.confirmLoginOut();
      }

      // open doc
      function openDoc() {
        openWindow(SITE_URL);
      }

      // 清除缓存
      async function clearCache() {
        const result = await refreshCache();
        const dragRes = await refreshDragCache();
        console.log('dragRes', dragRes);
        if (result.success) {
          const res = await queryAllDictItems();
          removeAuthCache(DB_DICT_DATA_KEY);
          setAuthCache(DB_DICT_DATA_KEY, res.result);
          createMessage.success(t('layout.header.refreshCacheComplete'));
          // 代码逻辑说明: 【issues/7433】vue3 数据字典优化建议
          userStore.setAllDictItems(res.result);
        } else {
          createMessage.error(t('layout.header.refreshCacheFailure'));
        }
      }
      // 切换部门
      function updateCurrentDepart() {
        loginSelectRef.value.show();
      }
      // 修改密码
      const updatePasswordRef = ref();
      // 代码逻辑说明: 【QQYUN-6333】空路由问题—首次访问资源太大
      async function updatePassword() {
        passwordVisible.value = true;
        await getRefPromise(updatePasswordRef);
        updatePasswordRef.value.show(userStore.getUserInfo.username);
      }
      function handleMenuClick(e: { key: MenuEvent }) {
        switch (e.key) {
          case 'logout':
            handleLoginOut();
            break;
          case 'doc':
            openDoc();
            break;
          case 'lock':
            handleLock();
            break;
          case 'cache':
            clearCache();
            break;
          case 'depart':
            updateCurrentDepart();
            break;
          case 'password':
            updatePassword();
            break;
          case 'account':
            // 代码逻辑说明: 进入用户设置页面------------
            go(`/system/usersetting`);
            break;
        }
      }

      return {
        prefixCls,
        t,
        getUserInfo,
        getAvatarUrl,
        handleMenuClick,
        getShowDoc,
        register,
        getUseLockPage,
        loginSelectRef,
        updatePasswordRef,
        passwordVisible,
        lockActionVisible,
        themeColorList,
        currentThemeColor,
        handleThemeColor,
      };
    },
  });
</script>
<style lang="less">
  @prefix-cls: ~'@{namespace}-header-user-dropdown';

  .@{prefix-cls} {
    height: @header-height;
    padding: 0 4px 0 4px;
    overflow: hidden;
    font-size: 12px;
    cursor: pointer;
    align-items: center;
    border-radius: 9px;
    transition: background-color var(--fast);

    &:hover {
      background-color: var(--surface-2);
    }

    img {
      width: 28px;
      height: 28px;
      margin-right: 8px;
    }

    &__header {
      border-radius: 50%;
    }

    &__name {
      font-size: 12.5px;
      font-weight: 600;
      color: var(--ink-900);
    }

    &-dropdown-overlay {
      // Override ant default padding/bg; our custom panel handles styling
      background: transparent !important;
      padding: 0 !important;
      box-shadow: none !important;
      border-radius: 12px;
      min-width: 220px !important;

      .ant-dropdown-menu {
        display: none !important;
      }
    }

    // Custom pop-style menu panel
    &-pop-menu {
      width: 220px;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 12px;
      box-shadow: var(--shadow-pop);
      padding: 6px;
      animation: pop-in 0.14s ease;

      &__head {
        display: flex;
        align-items: center;
        padding: 10px 12px 8px;
        font-size: 13px;
        font-weight: 600;
        color: var(--ink-900);
      }

      &__sep {
        height: 1px;
        background: var(--line);
        margin: 4px 0;
      }

      &__item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 10px;
        border-radius: 7px;
        cursor: pointer;
        color: var(--ink-700);
        font-size: 13px;
        font-family: inherit;
        border: 0;
        background: transparent;
        width: 100%;
        text-align: left;
        transition: background-color var(--fast);

        svg {
          width: 16px;
          height: 16px;
          color: var(--ink-500);
          flex-shrink: 0;
        }

        &:hover {
          background: var(--surface-2);
          color: var(--ink-900);
        }

        &--danger {
          color: var(--bad);

          svg {
            color: var(--bad);
          }

          &:hover {
            background: var(--bad-bg);
          }
        }
      }

      // Theme swatches row
      &__swatches {
        display: flex;
        gap: 8px;
        padding: 8px 12px 10px;
        flex-wrap: wrap;
      }

      &__swatch {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        cursor: pointer;
        border: 2px solid transparent;
        transition: transform var(--fast);
        position: relative;
        flex-shrink: 0;

        &:hover {
          transform: scale(1.1);
        }

        &.active {
          border-color: var(--ink-300);
          box-shadow: 0 0 0 2px var(--surface);

          &::after {
            content: '';
            position: absolute;
            inset: 3px;
            border-radius: 50%;
            border: 1.5px solid #fff;
          }
        }
      }
    }
  }

  @keyframes pop-in {
    from { opacity: 0; transform: translateY(-4px); }
    to { opacity: 1; transform: none; }
  }
</style>
