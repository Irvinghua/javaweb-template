<!--
  账户设置（个人信息中心）外壳
  UI Redesign: 按 jeecgboot-ui/pages/profile.html 重做布局：
    - 左侧 232px 子菜单（.profile-sidenav，sticky，rounded button + brand-50 active）
    - 右侧 .profile-content 区，动态渲染 BaseSetting / TenantSetting / AccountSetting / WeChatDingSetting
  业务逻辑（settingList 来源、组件切换 activeKey、tenantSetting 自动定位）完全保留。
-->
<template>
  <ScrollContainer>
    <div class="profile-layout" :class="prefixCls">
      <!-- ===== 左侧子菜单 ===== -->
      <aside class="profile-sidenav" role="tablist" aria-label="个人信息中心">
        <button
          v-for="item in componentList"
          :key="item.key"
          class="pn-item"
          :class="{ active: activeKey === item.key }"
          role="tab"
          :aria-selected="activeKey === item.key"
          @click="componentClick(item.key)"
        >
          <Icon :icon="item.icon" :size="18" />
          <span>{{ item.name }}</span>
        </button>
      </aside>

      <!-- ===== 右侧内容区 ===== -->
      <div class="profile-content">
        <template v-for="item in componentList" :key="item.key">
          <template v-if="activeKey === item.key">
            <component :is="item.component" v-if="!item.isSlot" />
            <slot name="component" v-if="item.isSlot" />
          </template>
        </template>
      </div>
    </div>
  </ScrollContainer>
</template>

<script lang="ts">
  import { ref, defineComponent, onMounted, computed } from 'vue';
  import { ScrollContainer } from '/@/components/Container';
  import { Icon } from '/@/components/Icon';
  import { settingList } from './UserSetting.data';
  import BaseSetting from './BaseSetting.vue';
  import AccountSetting from './AccountSetting.vue';
  import TenantSetting from './TenantSetting.vue';
  import WeChatDingSetting from './WeChatDingSetting.vue';
  import { useRouter } from 'vue-router';
  import { useDesign } from '/@/hooks/web/useDesign';

  export default defineComponent({
    components: {
      ScrollContainer,
      Icon,
      BaseSetting,
      AccountSetting,
      TenantSetting,
      WeChatDingSetting,
    },
    props: {
      componentList: {
        type: Array,
        default: settingList,
      },
    },
    setup() {
      const { prefixCls } = useDesign('user-account-setting-container');
      const activeKey = ref<string>('1');
      // 是否为 vip（保留旧逻辑，当前没有 vip 套餐时过滤掉 MyVipSetting）
      const showVip = ref<boolean>(false);
      const router = useRouter();
      const componentList = computed(() => {
        if (showVip.value) {
          return settingList;
        }
        return settingList.filter((item) => item.component != 'MyVipSetting');
      });

      function componentClick(key) {
        activeKey.value = key;
      }

      function goToMyTeantPage() {
        // 代码逻辑说明: 【QQYUN-5726】邀请加入租户加个按钮直接跳转过去
        const query = router.currentRoute.value.query;
        if (query && query.page === 'tenantSetting') {
          activeKey.value = '2';
        }
      }

      onMounted(() => {
        goToMyTeantPage();
      });

      return {
        prefixCls,
        componentList,
        componentClick,
        activeKey,
      };
    },
  });
</script>

<style lang="less" scoped>
  // ----------------------------------------------------
  // UI Redesign: 设计稿 profile.html .profile-layout
  // ----------------------------------------------------
  .profile-layout {
    display: grid;
    grid-template-columns: 232px 1fr;
    gap: 16px;
    align-items: start;
    padding: 22px 24px;
  }

  // 左侧子菜单 ----------------------------------------------
  .profile-sidenav {
    background: var(--surface, #fff);
    border-radius: var(--radius-card, 18px);
    box-shadow: var(--shadow-card, 0 2px 12px rgba(15, 23, 42, 0.05));
    padding: 14px 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    position: sticky;
    top: 22px;
  }

  .pn-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 14px;
    border-radius: 10px;
    color: var(--ink-700);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    border: 0;
    background: transparent;
    width: 100%;
    text-align: left;
    font-family: inherit;
    transition: background-color 0.16s ease, color 0.16s ease;

    .app-iconify,
    :deep(.app-iconify) {
      color: var(--ink-500);
      flex-shrink: 0;
    }

    &:hover {
      background: var(--surface-2, #f7f8fb);
      color: var(--ink-900);

      .app-iconify,
      :deep(.app-iconify) {
        color: var(--ink-700);
      }
    }

    &.active {
      background: var(--accent-50, rgba(91, 108, 255, 0.08));
      color: var(--accent-600, #4f5edb);
      font-weight: 600;

      .app-iconify,
      :deep(.app-iconify) {
        color: var(--accent, #5b6cff);
      }
    }
  }

  // 右侧内容区 ----------------------------------------------
  .profile-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
    min-width: 0;
  }

  // 响应式：窄屏左导航横向滚动
  @media (max-width: 960px) {
    .profile-layout {
      grid-template-columns: 1fr;
    }
    .profile-sidenav {
      flex-direction: row;
      overflow-x: auto;
      position: static;
      padding: 8px;
      gap: 4px;
    }
    .pn-item {
      flex-shrink: 0;
      width: auto;
      padding: 9px 14px;
    }
  }
</style>
