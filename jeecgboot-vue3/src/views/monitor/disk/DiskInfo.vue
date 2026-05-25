<!--
  UI Redesign: 设计稿 .disk-monitor 风格 —— 每个磁盘一张卡片，
  内含 270° 渐变仪表盘 + 右侧三块统计行（总容量/已使用/可用）。
  原来一行 4 个挤在一起的小仪表盘改成单列大卡，可读性更好；
  数据接口 queryDiskInfo / item.restPPT 计算逻辑不动。
-->
<template>
  <Skeleton v-if="spinning" active />
  <div v-else class="disk-info-list">
    <template v-if="diskInfo && diskInfo.length > 0">
      <gauge
        v-for="(item, index) in diskInfo"
        :key="'diskInfo' + index"
        :data="item"
      />
    </template>
  </div>
</template>
<script lang="ts" setup>
  import { onMounted, ref } from 'vue';
  import { Skeleton } from 'ant-design-vue';
  import { queryDiskInfo } from './disk.api';
  import gauge from './gauge.vue';

  const diskInfo = ref([]);
  const spinning = ref(true);

  function loadRedisInfo() {
    queryDiskInfo()
      .then((res) => {
        for (let i = 0; i < res.length; i++) {
          // 当前算法算的是磁盘的已使用空间
          res[i].restPPT = 100 - parseInt(String((res[i].rest / res[i].max) * 100));
        }
        diskInfo.value = res;
      })
      .finally(() => (spinning.value = false));
  }

  onMounted(() => {
    loadRedisInfo();
  });
</script>
<style lang="less" scoped>
  .disk-info-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 8px 0;
  }
</style>
