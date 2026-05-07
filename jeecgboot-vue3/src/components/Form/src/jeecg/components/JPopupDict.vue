<!--popup组件-->
<template>
  <div class="JPopupDict components-input-demo-presuffix">
    <!--输入框-->
    <a-select v-model:value="showText" v-bind="attrs" :mode="multi ? 'multiple' : ''" @click="handleOpen" readOnly :loading="loading">
      <a-select-option v-for="item in options" :value="item.value">{{ item.text }}</a-select-option>
    </a-select>
  </div>
</template>
<script lang="ts">
  import { defineComponent, ref, nextTick, watch } from 'vue';
  import { propTypes } from '/@/utils/propTypes';
  import { useAttrs } from '/@/hooks/core/useAttrs';
  import { useMessage } from '/@/hooks/web/useMessage';
  export default defineComponent({
    name: 'JPopupDict',
    inheritAttrs: false,
    props: {
      /**
       * 示例：demo,name,id
       * demo: online报表编码
       * name: online报表的字段，用户显示的label
       * id: online报表的字段，用于存储key
       */
      dictCode: propTypes.string.def(''),
      value: propTypes.string.def(''),
      sorter: propTypes.string.def(''),
      multi: propTypes.bool.def(false),
      param: propTypes.object.def({}),
      spliter: propTypes.string.def(','),
      getFormValues: propTypes.func,
      getContainer: propTypes.func,
      showAdvancedButton: propTypes.bool.def(true),
    },
    emits: ['update:value', 'register', 'change'],
    setup(props, { emit }) {
      const { createMessage } = useMessage();
      const attrs = useAttrs();
      const showText = ref<any>(props.multi ? [] : '');
      const options = ref<any>([]);
      const loading = ref(false);
      const code = props.dictCode.split(',')[0];
      const labelFiled = props.dictCode.split(',')[1];
      const valueFiled = props.dictCode.split(',')[2];
      if (!code || !valueFiled || !labelFiled) {
        createMessage.error('popupDict参数未正确配置!');
      }

      /**
       * 打开pop弹出框
       */
      function handleOpen() {
        // Online 报表弹窗已移除
      }
      /**
       * 监听value数值
       */
      watch(
        () => props.value,
        (val) => {
          if (props.multi) {
            showText.value = val && val.length > 0 ? val.split(props.spliter) : [];
          } else {
            showText.value = val ?? '';
          }
        },
        { immediate: true }
      );
      watch(
        () => showText.value,
        (val) => {
          let result;
          if (props.multi) {
            result = val.join(',');
          } else {
            result = val;
          }
          nextTick(() => {
            emit('change', result);
            emit('update:value', result);
          });
        }
      );
      /**
       * 传值回调
       */
      function callBack(rows) {
        const dataOptions: any = [];
        const dataValue: any = [];
        let result;
        rows.forEach((item) => {
          dataOptions.push({ value: item[valueFiled], text: item[labelFiled] });
          dataValue.push(item[valueFiled]);
        });
        options.value = dataOptions;
        if (props.multi) {
          showText.value = dataValue;
          result = dataValue.join(props.spliter);
        } else {
          showText.value = dataValue[0];
          result = dataValue[0];
        }
        nextTick(() => {
          emit('change', result);
          emit('update:value', result);
        });
      }

      return {
        showText,
        attrs,
        handleOpen,
        callBack,
        code,
        options,
        loading,
        valueFiled,
      };
    },
  });
</script>
<style lang="less" scoped>
  // 代码逻辑说明: 【QQYUN-9260】必填模式下会影响到弹窗内antd组件的样式
  .JPopupDict {
    > .ant-form-item {
      display: none;
    }
  }
  .components-input-demo-presuffix {
    :deep(.ant-select-dropdown) {
      display: none !important;
    }
  }
  .components-input-demo-presuffix .anticon-close-circle {
    cursor: pointer;
    color: #ccc;
    transition: color 0.3s;
    font-size: 12px;
  }

  .components-input-demo-presuffix .anticon-close-circle:hover {
    color: #f5222d;
  }

  .components-input-demo-presuffix .anticon-close-circle:active {
    color: #666;
  }
</style>
