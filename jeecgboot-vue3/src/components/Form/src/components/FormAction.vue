<template>
  <a-col v-bind="actionColOpt" v-if="showActionButtonGroup">
    <div class="btnArea" style="width: 100%" :style="{ textAlign: actionColOpt.style.textAlign }">
      <FormItem>
        <slot name="submitBefore"></slot>
        <Button type="primary" class="mr-2 form-action-submit-btn" v-bind="getSubmitBtnOptions" @click="submitAction" v-if="showSubmitButton">
          {{ getSubmitBtnOptions.text }}
        </Button>

        <slot name="resetBefore"></slot>
        <Button type="default" class="mr-2 form-action-reset-btn" v-bind="getResetBtnOptions" @click="resetAction" v-if="showResetButton">
          {{ getResetBtnOptions.text }}
        </Button>

        <slot name="advanceBefore"></slot>
        <button
          v-if="showAdvancedButton && !hideAdvanceBtn"
          class="form-filter-toggle"
          :class="{ 'is-expanded': isAdvanced }"
          type="button"
          @click="toggleAdvanced"
        >
          高级筛选
          <svg class="form-filter-toggle__chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>
        <slot name="advanceAfter"></slot>
      </FormItem>
    </div>
  </a-col>
</template>
<script lang="ts">
  import type { ColEx } from '../types/index';
  //import type { ButtonProps } from 'ant-design-vue/es/button/buttonTypes';
  import { defineComponent, computed, PropType } from 'vue';
  import { Form, Col } from 'ant-design-vue';
  import { Button, ButtonProps } from '/@/components/Button';
  import { BasicArrow } from '/@/components/Basic';
  import { useFormContext } from '../hooks/useFormContext';
  import { useI18n } from '/@/hooks/web/useI18n';
  import { propTypes } from '/@/utils/propTypes';

  type ButtonOptions = Partial<ButtonProps> & { text: string };

  export default defineComponent({
    name: 'BasicFormAction',
    components: {
      FormItem: Form.Item,
      Button,
      BasicArrow,
      [Col.name]: Col,
    },
    props: {
      showActionButtonGroup: propTypes.bool.def(true),
      showResetButton: propTypes.bool.def(true),
      showSubmitButton: propTypes.bool.def(true),
      showAdvancedButton: propTypes.bool.def(true),
      resetButtonOptions: {
        type: Object as PropType<ButtonOptions>,
        default: () => ({}),
      },
      submitButtonOptions: {
        type: Object as PropType<ButtonOptions>,
        default: () => ({}),
      },
      actionColOptions: {
        type: Object as PropType<Partial<ColEx>>,
        default: () => ({}),
      },
      actionSpan: propTypes.number.def(6),
      isAdvanced: propTypes.bool,
      hideAdvanceBtn: propTypes.bool,
      layout: propTypes.oneOf(['horizontal', 'vertical', 'inline']).def('horizontal'),
    },
    emits: ['toggle-advanced'],
    setup(props, { emit }) {
      const { t } = useI18n();

      const actionColOpt = computed(() => {
        const { showAdvancedButton, actionSpan: span, actionColOptions } = props;
        const actionSpan = 24 - span;
        const advancedSpanObj = showAdvancedButton ? { span: actionSpan < 6 ? 24 : actionSpan } : {};
        // 代码逻辑说明: 【QQYUN-6566】BasicForm支持一行显示(inline)
        const defaultSpan = props.layout == 'inline' ? {} : { span: showAdvancedButton ? 6 : 4 };
        const actionColOpt: Partial<ColEx> = {
          style: { textAlign: 'right' },
          ...defaultSpan,
          ...advancedSpanObj,
          ...actionColOptions,
        };
        
        
        
        return actionColOpt;
      });

      const getResetBtnOptions = computed((): ButtonOptions => {
        return Object.assign(
          {
            text: t('common.resetText'),
            preIcon: 'ic:baseline-restart-alt',
          },
          props.resetButtonOptions
        );
      });

      const getSubmitBtnOptions = computed(() => {
        return Object.assign(
          {},
          {
            text: t('common.queryText'),
            preIcon: 'ant-design:search-outlined',
          },
          props.submitButtonOptions
        );
      });

      function toggleAdvanced() {
        emit('toggle-advanced');
      }

      return {
        t,
        actionColOpt,
        getResetBtnOptions,
        getSubmitBtnOptions,
        toggleAdvanced,
        ...useFormContext(),
      };
    },
  });
</script>
<style lang="less" scoped>
  // 代码逻辑说明: 【TV360X-999】在1753px宽度下 流程设计页面查询的展开换行了
  .btnArea {
    :deep(.ant-form-item-control-input-content) {
      display: flex;
      align-items: center;
      .ant-btn-link {
        padding-left: 0;
      }
    }
  }

  /* 查询/重置按钮美化 */
  :deep(.form-action-submit-btn) {
    background: linear-gradient(135deg, var(--accent), var(--accent-600));
    border-color: transparent;
    box-shadow: 0 4px 12px rgba(91, 108, 255, 0.28);
    font-weight: 500;
    transition: box-shadow var(--fast), opacity var(--fast);

    &:hover,
    &:focus {
      box-shadow: 0 6px 16px rgba(91, 108, 255, 0.38);
      opacity: 0.92;
    }
  }

  :deep(.form-action-reset-btn) {
    background: var(--surface);
    border-color: var(--line-strong);
    color: var(--ink-700);
    font-weight: 500;
    transition: background-color var(--fast), color var(--fast);

    &:hover,
    &:focus {
      background: var(--surface-2);
      color: var(--ink-900);
      border-color: var(--line-strong);
    }
  }

  /* 高级筛选切换按钮 */
  .form-filter-toggle {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: transparent;
    border: 0;
    color: var(--accent);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    padding: 0 6px;
    font-family: inherit;
    line-height: 1;
    transition: opacity var(--fast);

    &:hover {
      opacity: 0.8;
    }

    &__chevron {
      width: 13px;
      height: 13px;
      transition: transform var(--norm);
      flex-shrink: 0;
    }

    &.is-expanded &__chevron {
      transform: rotate(180deg);
    }
  }
</style>
