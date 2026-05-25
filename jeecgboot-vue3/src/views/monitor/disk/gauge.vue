<template>
  <!--
    UI Redesign: 磁盘使用率仪表盘 + 右侧统计卡（设计稿 .disk-monitor）
    - 仪表盘 270° 环形弧线，渐变色描边
    - 中心大字百分比，下方 13px 小字 "磁盘使用率"
    - 右侧三块 stat 行：总容量 / 已使用 / 可用空间，13px label + 15px tabular value
    业务逻辑：data.name / data.max / data.rest / data.restPPT 不动
  -->
  <div class="disk-card">
    <div class="disk-card__title" v-if="data && data.name">{{ data.name }}</div>
    <div class="disk-monitor">
      <div ref="chartRef" class="disk-gauge" />
      <div class="disk-stats">
        <div class="disk-stat">
          <span class="dot-mark" style="background: var(--accent)"></span>
          <span class="ds-label">磁盘总容量</span>
          <span class="ds-value">{{ formatBytes(data.max) }}</span>
        </div>
        <div class="disk-stat">
          <span class="dot-mark" style="background: #D97706"></span>
          <span class="ds-label">已使用空间</span>
          <span class="ds-value">{{ usedDisplay }}</span>
        </div>
        <div class="disk-stat">
          <span class="dot-mark" style="background: var(--good, #15A34A)"></span>
          <span class="ds-label">可用空间</span>
          <span class="ds-value">{{ formatBytes(data.rest) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script lang="ts" setup>
  import { onMounted, ref, reactive, computed, Ref } from 'vue';
  import { useECharts } from '/@/hooks/web/useECharts';
  import { GaugeChart } from 'echarts/charts';

  const props = defineProps({ data: { type: Object, default: () => ({}) } });
  const chartRef = ref<HTMLDivElement | null>(null);
  const { setOptions, echarts } = useECharts(chartRef as Ref<HTMLDivElement>);

  // UI Redesign: 270° 弧线 + 渐变 + 居中百分比的清爽仪表盘
  // 业务上 restPPT 是 "已使用率"（原代码 100 - rest/max*100），保留语义不变
  const option = reactive<any>({
    series: [
      {
        type: 'gauge',
        startAngle: 225,
        endAngle: -45,
        min: 0,
        max: 100,
        radius: '92%',
        // 内圈描边轨道
        axisLine: {
          lineStyle: {
            width: 14,
            color: [[1, '#F1F3F8']],
          },
        },
        // 已使用进度（渐变描边）
        progress: {
          show: true,
          width: 14,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 1, y2: 1,
              colorStops: [
                { offset: 0, color: '#7E8DFF' },
                { offset: 1, color: '#5B6CFF' },
              ],
            },
          },
        },
        pointer: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        anchor: { show: false },
        // 中心数字 + 副标题
        detail: {
          valueAnimation: true,
          formatter: '{value}%',
          fontSize: 36,
          fontWeight: 700,
          color: '#0F172A',
          offsetCenter: [0, '-6%'],
        },
        title: {
          show: true,
          offsetCenter: [0, '36%'],
          fontSize: 13,
          color: '#64748B',
          fontWeight: 400,
        },
        data: [
          {
            value: 0,
            name: '磁盘使用率',
          },
        ],
      },
    ],
  });

  /**
   * Bytes → 人类可读单位 (B / KB / MB / GB / TB / PB)
   * - 入参可能是 number 或 number string；非数字时原样回显
   * - 1024 进制，保留 2 位小数（小于 1KB 时显示整数 Byte）
   */
  function formatBytes(input: number | string | undefined | null): string {
    if (input == null || input === '') return '--';
    const n = typeof input === 'number' ? input : Number(input);
    if (!Number.isFinite(n)) return String(input); // 已经是 "512GB" 这类字符串就别动它
    if (n <= 0) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
    const i = Math.min(Math.floor(Math.log(n) / Math.log(1024)), units.length - 1);
    const value = n / Math.pow(1024, i);
    // <1KB 整数显示，其它保留 2 位小数；末尾零去掉避免 "1.00 GB" 这种
    const display = i === 0 ? String(Math.round(value)) : value.toFixed(2).replace(/\.?0+$/, '');
    return `${display} ${units[i]}`;
  }

  // 已使用空间 = total - rest（两者都是字节数时优先精确计算，否则退化为百分比）
  const usedDisplay = computed(() => {
    const max = Number(props.data?.max);
    const rest = Number(props.data?.rest);
    if (Number.isFinite(max) && Number.isFinite(rest) && max > 0) {
      return formatBytes(max - rest);
    }
    if (props.data?.restPPT != null) {
      return `${props.data.restPPT}%`;
    }
    return '--';
  });

  function initCharts() {
    option.series[0].data[0].value = props.data?.restPPT ?? 0;
    setOptions(option);
  }

  onMounted(() => {
    echarts.use(GaugeChart);
    initCharts();
  });
</script>
<style lang="less" scoped>
  .disk-card {
    background: var(--surface, #fff);
    border: 1px solid var(--line, rgba(15, 23, 42, 0.07));
    border-radius: var(--radius-card, 18px);
    padding: 18px 22px 22px;

    &__title {
      font-size: 14px;
      font-weight: 600;
      color: var(--ink-900);
      margin-bottom: 6px;
    }
  }

  .disk-monitor {
    display: flex;
    align-items: center;
    gap: 32px;
    flex-wrap: wrap;
    padding: 8px 0 0;
  }

  .disk-gauge {
    width: 240px;
    height: 220px;
    flex-shrink: 0;
  }

  .disk-stats {
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-width: 220px;
    flex: 1;
  }

  .disk-stat {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 16px;
    background: var(--surface-2, #F7F8FB);
    border-radius: var(--radius-ctrl, 10px);
  }

  .dot-mark {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .ds-label {
    font-size: 13px;
    color: var(--ink-500);
    flex: 1;
  }

  .ds-value {
    font-size: 15px;
    font-weight: 700;
    color: var(--ink-900);
    font-variant-numeric: tabular-nums;
  }
</style>
