<!--
 * @Author: Vben
 * @Description: Multi-language switching component
-->
<template>
  <Dropdown :trigger="['click']" placement="bottomRight" overlayClassName="app-locale-picker-overlay">
    <span class="cursor-pointer flex items-center">
      <Icon icon="ion:language" />
      <span v-if="showText" class="ml-1">{{ getLocaleText }}</span>
    </span>
    <template #overlay>
      <div class="locale-pop">
        <div
          v-for="item in localeList"
          :key="item.event"
          class="locale-pop__item"
          :class="{ 'locale-pop__item--active': selectedKeys[0] === item.event }"
          @click="handleMenuEvent(item)"
        >
          <svg
            class="locale-pop__icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <path d="M2 12h20" />
            <path d="M12 2a15 15 0 0 1 0 20" />
            <path d="M12 2a15 15 0 0 0 0 20" />
          </svg>
          <span class="locale-pop__text">{{ item.text }}</span>
          <svg
            v-if="selectedKeys[0] === item.event"
            class="locale-pop__check"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="3"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
      </div>
    </template>
  </Dropdown>
</template>
<script lang="ts" setup>
  import type { LocaleType } from '/#/config';
  import type { DropMenu } from '/@/components/Dropdown';
  import { ref, watchEffect, unref, computed } from 'vue';
  import { Dropdown } from 'ant-design-vue';
  import { Icon } from '/@/components/Icon';
  import { useLocale } from '/@/locales/useLocale';
  import { localeList } from '/@/settings/localeSetting';

  const props = defineProps({
    /**
     * Whether to display text
     */
    showText: { type: Boolean, default: true },
    /**
     * Whether to refresh the interface when changing
     */
    reload: { type: Boolean },
  });

  const selectedKeys = ref<string[]>([]);

  const { changeLocale, getLocale } = useLocale();

  const getLocaleText = computed(() => {
    const key = selectedKeys.value[0];
    if (!key) {
      return '';
    }
    return localeList.find((item) => item.event === key)?.text;
  });

  watchEffect(() => {
    selectedKeys.value = [unref(getLocale)];
  });

  async function toggleLocale(lang: LocaleType | string) {
    await changeLocale(lang as LocaleType);
    selectedKeys.value = [lang as string];
    props.reload && location.reload();
  }

  function handleMenuEvent(menu: DropMenu) {
    if (unref(getLocale) === menu.event) {
      return;
    }
    toggleLocale(menu.event as string);
  }
</script>

<style lang="less">
  /* AntD dropdown 外壳中性化，真正面板由 .locale-pop 承担 */
  .app-locale-picker-overlay {
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;

    .ant-dropdown-menu {
      display: none !important;
    }
  }

  /* 语言下拉面板 —— 对齐设计稿 #langPop / .pop */
  .locale-pop {
    min-width: 160px;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 12px;
    box-shadow: var(--shadow-pop);
    padding: 6px;
    animation: locale-pop-in 0.14s ease;

    &__item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 10px;
      border-radius: 7px;
      cursor: pointer;
      color: var(--ink-700);
      font-size: 13px;
      transition: background-color var(--fast), color var(--fast);

      &:hover {
        background: var(--surface-2);
        color: var(--ink-900);
      }

      &--active {
        color: var(--accent);
      }
    }

    &__icon {
      width: 16px;
      height: 16px;
      color: var(--ink-500);
      flex-shrink: 0;
    }

    &__item--active &__icon {
      color: var(--accent);
    }

    &__text {
      flex: 1;
    }

    &__check {
      width: 15px;
      height: 15px;
      color: var(--accent);
      margin-left: auto;
      flex-shrink: 0;
    }
  }

  @keyframes locale-pop-in {
    from {
      opacity: 0;
      transform: translateY(-4px);
    }
    to {
      opacity: 1;
      transform: none;
    }
  }
</style>
