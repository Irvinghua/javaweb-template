<template>
  <div :class="prefixCls" :style="getStyle" v-if="showFooter || $slots.footer">
    <template v-if="!$slots.footer">
      <slot name="insertFooter"></slot>
      <a-button v-bind="cancelButtonProps" @click="handleClose" class="mr-2" v-if="showCancelBtn">
        {{ cancelText }}
      </a-button>
      <slot name="centerFooter"></slot>
      <a-button :type="okType" @click="handleOk" v-bind="okButtonProps" class="mr-2" :loading="confirmLoading" v-if="showOkBtn">
        {{ okText }}
      </a-button>
      <slot name="appendFooter"></slot>
    </template>

    <template v-else>
      <slot name="footer"></slot>
    </template>
  </div>
</template>
<script lang="ts">
  import type { CSSProperties } from 'vue';
  import { defineComponent, computed } from 'vue';
  import { useDesign } from '/@/hooks/web/useDesign';

  import { footerProps } from '../props';
  export default defineComponent({
    name: 'BasicDrawerFooter',
    props: {
      ...footerProps,
      height: {
        type: String,
        default: '60px',
      },
    },
    emits: ['ok', 'close'],
    setup(props, { emit }) {
      const { prefixCls } = useDesign('basic-drawer-footer');

      const getStyle = computed((): CSSProperties => {
        const heightStr = `${props.height}`;
        return {
          height: heightStr,
          lineHeight: heightStr,
        };
      });

      function handleOk() {
        emit('ok');
      }

      function handleClose() {
        emit('close');
      }
      return { handleOk, prefixCls, handleClose, getStyle };
    },
  });
</script>

<style lang="less">
  // UI Redesign: DrawerFooter 换皮
  // 详细按钮样式由全局 modal-drawer.less (.jeecg-basic-drawer-footer) 控制
  @prefix-cls: ~'@{namespace}-basic-drawer-footer';
  .@{prefix-cls} {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
    padding: 13px 20px;
    background: var(--surface);
    border-top: 1px solid var(--line);
    // 高度由内容撑开（auto），覆盖组件通过 getStyle 设置的 height/lineHeight
    height: auto !important;
    line-height: normal !important;

    > * {
      margin-right: 0;
    }
  }
</style>
