<!--
 * @Author: Jeecg
 * @Description: logo component
-->
<template>
  <div class="anticon" :class="getAppLogoClass" @click="goHome">
    <img src="../../../assets/images/logo.png" />
    <div class="ml-2 truncate md:opacity-100" :class="getTitleClass" v-show="showTitle">
      {{ shortTitle }}
    </div>
  </div>
</template>
<script lang="ts" setup>
  import { computed, unref } from 'vue';
  import { useGlobSetting } from '/@/hooks/setting';
  import { useGo } from '/@/hooks/web/usePage';
  import { useMenuSetting } from '/@/hooks/setting/useMenuSetting';
  import { useDesign } from '/@/hooks/web/useDesign';
  import { PageEnum } from '/@/enums/pageEnum';
  import { useUserStore } from '/@/store/modules/user';

  const props = defineProps({
    /**
     * The theme of the current parent component
     */
    theme: { type: String, validator: (v: string) => ['light', 'dark'].includes(v) },
    /**
     * Whether to show title
     */
    showTitle: { type: Boolean, default: true },
    /**
     * The title is also displayed when the menu is collapsed
     */
    alwaysShowTitle: { type: Boolean },
  });

  const { prefixCls } = useDesign('app-logo');
  const { getCollapsedShowTitle } = useMenuSetting();
  const userStore = useUserStore();
  const { shortTitle } = useGlobSetting();
  
  const go = useGo();

  const getAppLogoClass = computed(() => [prefixCls, props.theme, { 'collapsed-show-title': unref(getCollapsedShowTitle) }]);

  const getTitleClass = computed(() => [
    `${prefixCls}__title`,
    {
      'xs:opacity-0': !props.alwaysShowTitle,
    },
  ]);

  function goHome() {
    go(userStore.getUserInfo.homePath || PageEnum.BASE_HOME);
  }
</script>
<style lang="less" scoped>
  @prefix-cls: ~'@{namespace}-app-logo';

  .@{prefix-cls} {
    display: flex;
    align-items: center;
    padding: 4px 14px 18px 14px;
    cursor: pointer;
    transition: all 0.2s ease;
    gap: 10px;
    border-bottom: none !important;

    // Sidebar logo area: white bg, no gradient
    &.jeecg-layout-mix-sider-logo,
    &.jeecg-layout-menu-logo {
      background: var(--surface) !important;
    }

    // The logo image: render as accent-colored square
    img {
      width: 34px !important;
      height: 34px !important;
      border-radius: 10px;
      background: var(--accent);
      object-fit: contain;
      padding: 4px;
      filter: brightness(0) invert(1);
    }

    // Collapsed state: center the icon
    &.collapsed-show-title {
      padding-left: 10px;
      padding-right: 10px;
      justify-content: center;
    }

    &.light &__title {
      color: var(--ink-900);
      font-size: 17px;
      font-weight: 700;
      letter-spacing: 0.1px;
    }

    &.dark &__title {
      color: @white;
    }

    &__title {
      font-size: 17px;
      font-weight: 700;
      transition: all 0.3s;
      line-height: normal;
      color: var(--ink-900);
    }
  }
</style>
