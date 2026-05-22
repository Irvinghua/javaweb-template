<template>
  <Teleport to="body">
    <transition name="zoom-fade" mode="out-in">
      <div :class="getClass" @click.stop v-if="visible">
        <div :class="`${prefixCls}-content`" v-click-outside="handleClose">
          <div :class="`${prefixCls}-input__wrapper`">
            <a-input :class="`${prefixCls}-input`" :placeholder="t('common.searchText')" ref="inputRef" allow-clear @change="handleSearch">
              <template #prefix>
                <SearchOutlined />
              </template>
            </a-input>
            <span :class="`${prefixCls}-cancel`" @click="handleClose">Esc</span>
          </div>

          <div :class="`${prefixCls}-not-data`" v-show="getIsNotData">
            {{ t('component.app.searchNotData') }}
          </div>

          <ul :class="`${prefixCls}-list`" v-show="!getIsNotData" ref="scrollWrap">
            <li
              :ref="setRefs(index)"
              v-for="(item, index) in searchResult"
              :key="item.path"
              :data-index="index"
              @mouseenter="handleMouseenter"
              @click="handleEnter"
              :class="[
                `${prefixCls}-list__item`,
                {
                  [`${prefixCls}-list__item--active`]: activeIndex === index,
                },
              ]"
            >
              <div :class="`${prefixCls}-list__item-icon`">
                <Icon :icon="item.icon || 'mdi:form-select'" :size="20" />
              </div>
              <div :class="`${prefixCls}-list__item-text`">
                {{ item.name }}
              </div>
              <div :class="`${prefixCls}-list__item-enter`">
                <Icon icon="ant-design:enter-outlined" :size="20" />
              </div>
            </li>
          </ul>
          <AppSearchFooter />
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script lang="ts" setup>
  import { computed, unref, ref, watch, nextTick } from 'vue';
  import { SearchOutlined } from '@ant-design/icons-vue';
  import AppSearchFooter from './AppSearchFooter.vue';
  import Icon from '/@/components/Icon';
  // @ts-ignore
  import vClickOutside from '/@/directives/clickOutside';
  import { useDesign } from '/@/hooks/web/useDesign';
  import { useRefs } from '/@/hooks/core/useRefs';
  import { useMenuSearch } from './useMenuSearch';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { useAppInject } from '/@/hooks/web/useAppInject';

  const props = defineProps({
    visible: { type: Boolean },
  });

  const emit = defineEmits(['close']);

  const scrollWrap = ref(null);
  const inputRef = ref<Nullable<HTMLElement>>(null);

  const { t } = useI18n();
  const { prefixCls } = useDesign('app-search-modal');
  const [refs, setRefs] = useRefs();
  const { getIsMobile } = useAppInject();

  const { handleSearch, searchResult, keyword, activeIndex, handleEnter, handleMouseenter } = useMenuSearch(refs, scrollWrap, emit);

  const getIsNotData = computed(() => !keyword || unref(searchResult).length === 0);

  const getClass = computed(() => {
    return [
      prefixCls,
      {
        [`${prefixCls}--mobile`]: unref(getIsMobile),
      },
    ];
  });

  watch(
    () => props.visible,
    (visible: boolean) => {
      visible &&
        nextTick(() => {
          unref(inputRef)?.focus();
        });
    }
  );

  function handleClose() {
    searchResult.value = [];
    emit('close');
  }
</script>
<style lang="less" scoped>
  @prefix-cls: ~'@{namespace}-app-search-modal';
  @footer-prefix-cls: ~'@{namespace}-app-search-footer';
  .@{prefix-cls} {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 800;
    display: flex;
    width: 100%;
    height: 100%;
    // cmd-overlay style: backdrop blur
    padding: 14vh 16px 16px;
    background-color: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(2px);
    -webkit-backdrop-filter: blur(2px);
    justify-content: center;
    align-items: flex-start;

    &--mobile {
      padding: 0;

      > div {
        width: 100%;
      }

      .@{prefix-cls}-input {
        width: calc(100% - 38px);
      }

      .@{prefix-cls}-cancel {
        display: inline-block;
      }

      .@{prefix-cls}-content {
        width: 100%;
        height: 100%;
        border-radius: 0;
        max-height: 100vh;
      }

      .@{footer-prefix-cls} {
        display: none;
      }

      .@{prefix-cls}-list {
        height: calc(100% - 80px);
        max-height: unset;

        &__item {
          &-enter {
            opacity: 0 !important;
          }
        }
      }
    }

    // cmd-panel style
    &-content {
      position: relative;
      width: 100%;
      max-width: 560px;
      margin: 0 auto;
      background: var(--surface);
      border-radius: 14px;
      box-shadow: 0 24px 64px -12px rgba(15, 23, 42, 0.28);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      max-height: 60vh;
    }

    // cmd-search style — replaces the old input wrapper
    &-input__wrapper {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
      flex-shrink: 0;

      .@{prefix-cls}-cancel {
        font-size: 11px;
        color: var(--ink-500);
        background: var(--surface-2);
        padding: 3px 8px;
        border-radius: 5px;
        cursor: pointer;
        white-space: nowrap;
        display: block; // always show as "Esc" hint
      }
    }

    &-input {
      flex: 1;
      min-width: 0;
      height: 36px;
      font-size: 14px;
      color: var(--ink-900);
      border: none !important;
      background: transparent !important;
      box-shadow: none !important;
      padding: 0;

      :deep(.ant-input) {
        background: transparent;
        border: none;
        box-shadow: none;
        font-size: 14px;
        color: var(--ink-900);
        padding: 0;

        &::placeholder {
          color: var(--ink-400);
        }
      }

      :deep(.ant-input-prefix) {
        margin-right: 8px;
      }

      span[role='img'] {
        color: var(--ink-400);
        font-size: 17px;
      }

      :deep(.ant-input-clear-icon) {
        color: var(--ink-400);
      }
    }

    &-not-data {
      display: flex;
      width: 100%;
      padding: 30px 16px;
      font-size: 13px;
      color: var(--ink-400);
      align-items: center;
      justify-content: center;
    }

    // cmd-results style
    &-list {
      flex: 1;
      max-height: none;
      padding: 6px;
      margin: 0;
      overflow-y: auto;
      overflow-x: hidden;

      &__item {
        position: relative;
        display: flex;
        width: 100%;
        height: auto;
        min-height: 44px;
        padding: 9px 10px;
        margin-top: 0;
        margin-bottom: 0;
        font-size: 13px;
        color: var(--ink-700);
        cursor: pointer;
        border-radius: 8px;
        box-shadow: none;
        align-items: center;
        gap: 10px;
        transition: background-color var(--fast);

        > div:first-child,
        > div:last-child {
          display: flex;
          align-items: center;
        }

        &:hover,
        &--active {
          background: var(--accent-50);
          color: var(--accent);
          box-shadow: none;

          :deep(svg) {
            color: var(--accent) !important;
          }
        }

        &-icon {
          width: 24px;
          flex-shrink: 0;
          color: var(--ink-500);

          :deep(svg) {
            width: 15px;
            height: 15px;
          }
        }

        &-text {
          flex: 1;
        }

        &-enter {
          width: 24px;
          opacity: 0;
          color: var(--ink-400);

          :deep(svg) {
            width: 15px;
            height: 15px;
          }
        }
      }
    }
  }
</style>
