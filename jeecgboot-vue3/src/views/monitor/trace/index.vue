<template>
  <div class="p-4">
    <BasicTable @register="registerTable" :dataSource="dataSource" @change="handlerTableChange">
      <template #tableTitle>
        <!-- UI Redesign: 设计稿 .refresh-line —— 13px / --ink-500，b 标签深色 --ink-900 -->
        <div class="trace-refresh-line">
          共追踪到 <b>{{ dataSource.length }}</b> 条近期 HTTP 请求记录
          <span class="dot">|</span>
          <a class="link-btn" @click="loadDate">立即刷新</a>
        </div>
      </template>
      <template #toolbar>
        <!-- UI Redesign: 状态过滤改用设计稿 .seg 胶囊段控件样式（RadioButtonGroup 被全局换肤过） -->
        <a-radio-group class="trace-status-tabs" v-model:value="query" @change="loadDate">
          <a-radio-button value="all">全部</a-radio-button>
          <a-radio-button value="success">成功</a-radio-button>
          <a-radio-button value="error">错误</a-radio-button>
        </a-radio-group>
      </template>
    </BasicTable>
  </div>
</template>
<script lang="ts" name="monitor-trace" setup>
  import { onMounted, ref, reactive } from 'vue';
  import { BasicTable, useTable, TableAction } from '/@/components/Table';
  import { getActuatorList } from './trace.api';
  import { columns } from './trace.data';
  import { useMessage } from '/@/hooks/web/useMessage';

  const dataSource = ref([]);
  const { createMessage } = useMessage();
  const query = ref('all');
  const order = ref('');

  const [registerTable, { reload }] = useTable({
    columns,
    showIndexColumn: false,
    bordered: true,
    rowKey: 'id',
  });

  function loadDate() {
    getActuatorList(query.value,order.value).then((res) => {
      let filterData = [];
      for (let d of res.traces) {
        if (d.request.method !== 'OPTIONS' && d.request.uri.indexOf('httptrace') === -1) {
          filterData.push(d);
        }
      }
      dataSource.value = filterData;
    });
  }

  const handlerTableChange = (args, arg1, sort, action) => {
    if ('sort' == action.action && sort.field) {
      order.value = sort.field;
      if (sort.order) {
        order.value += sort.order == 'ascend' ? '/asc' : '/desc';
      } else {
        order.value = '';
      }
    }
    loadDate();
  };

  onMounted(() => {
    loadDate();
  });
</script>
<style lang="less">
  // UI Redesign: 设计稿 .refresh-line
  .trace-refresh-line {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    color: var(--ink-500);
    flex-wrap: wrap;

    b {
      color: var(--ink-900);
      font-weight: 600;
    }
    .dot {
      color: var(--ink-300);
    }
    .link-btn {
      color: var(--accent);
      font-weight: 600;
      cursor: pointer;

      &:hover {
        text-decoration: underline;
      }
    }
  }

  // 状态过滤段控件：复用 .redesign-form .seg 风格（这里不在表单里所以单独刷一份）
  .trace-status-tabs.ant-radio-group {
    display: inline-flex;
    background: var(--surface-3);
    border-radius: 999px;
    padding: 3px;
    gap: 2px;
    border: 0;
    height: 32px;
    align-items: center;

    .ant-radio-button-wrapper {
      height: 24px;
      line-height: 24px;
      padding: 0 14px;
      border: 0 !important;
      background: transparent !important;
      font-size: 12px;
      font-weight: 600;
      color: var(--ink-500);
      border-radius: 999px !important;
      box-shadow: none !important;

      &::before {
        display: none !important;
      }
      &:hover {
        color: var(--ink-900);
      }
      &-checked {
        background: var(--surface) !important;
        color: var(--accent) !important;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.1) !important;
      }
    }
  }
</style>
