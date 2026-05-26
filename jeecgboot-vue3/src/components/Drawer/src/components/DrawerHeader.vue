<template>
  <BasicTitle v-if="!isDetail" :class="[prefixCls, 'is-drawer']">
    <slot name="title"></slot>
    {{ !$slots.title ? title : '' }}
  </BasicTitle>

  <div :class="[prefixCls, `${prefixCls}--detail`]" v-else>
    <span :class="`${prefixCls}__twrap`">
      <span @click="handleClose" v-if="showDetailBack">
        <ArrowLeftOutlined :class="`${prefixCls}__back`" />
      </span>
      <span v-if="title">{{ title }}</span>
    </span>

    <span :class="`${prefixCls}__toolbar`">
      <slot name="titleToolbar"></slot>
    </span>
  </div>
</template>
<script lang="ts">
  import { defineComponent } from 'vue';
  import { BasicTitle } from '/@/components/Basic';
  import { ArrowLeftOutlined } from '@ant-design/icons-vue';

  import { useDesign } from '/@/hooks/web/useDesign';

  import { propTypes } from '/@/utils/propTypes';
  export default defineComponent({
    name: 'BasicDrawerHeader',
    components: { BasicTitle, ArrowLeftOutlined },
    props: {
      isDetail: propTypes.bool,
      showDetailBack: propTypes.bool,
      title: propTypes.string,
    },
    emits: ['close'],
    setup(_, { emit }) {
      const { prefixCls } = useDesign('basic-drawer-header');

      function handleClose() {
        emit('close');
      }

      return { prefixCls, handleClose };
    },
  });
</script>

<style lang="less">
  // UI Redesign: DrawerHeader 换皮
  @prefix-cls: ~'@{namespace}-basic-drawer-header';
  .@{prefix-cls} {
    display: flex;
    height: 100%;
    align-items: center;
    font-size: 15px;
    font-weight: 600;
    color: var(--ink-900);

    &__back {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 8px;
      cursor: pointer;
      color: var(--ink-500);
      margin-right: 8px;
      transition: background-color var(--fast), color var(--fast);

      &:hover {
        background: var(--surface-3);
        color: var(--ink-700);
      }
    }

    &__twrap {
      flex: 1;
      min-width: 0;
    }

    &__toolbar {
      padding-right: 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
</style>
