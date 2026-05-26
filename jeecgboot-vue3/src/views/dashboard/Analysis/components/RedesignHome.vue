<template>
  <div class="rh-dashboard">
    <!-- 核心指标卡 -->
    <section class="rh-stats" aria-label="核心指标">
      <div v-for="card in statCards" :key="card.label" class="rh-stat-card">
        <div class="rh-stat-chip" :style="{ background: card.chipBg, color: card.chipFg }">
          <component :is="card.icon" class="rh-chip-icon" />
        </div>
        <div class="rh-stat-body">
          <div class="rh-stat-label">{{ card.label }}</div>
          <div class="rh-stat-value-row">
            <div class="rh-stat-value">{{ card.value }}</div>
            <span class="rh-delta" :class="card.trend === 'up' ? 'up' : 'down'">
              <svg v-if="card.trend === 'up'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="18 15 12 9 6 15" />
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9" />
              </svg>
              {{ card.delta }}
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- 中部行：销售额卡 + 促销卡 -->
    <section class="rh-mid-row">
      <!-- 销售额卡 -->
      <div class="rh-card">
        <div class="rh-card-header">
          <div class="rh-switcher" role="tablist">
            <button
              v-for="tab in chartTabs"
              :key="tab"
              :class="{ on: activeTab === tab }"
              role="tab"
              @click="activeTab = tab"
            >{{ tab }}</button>
          </div>
          <div class="rh-range">
            <button v-for="r in ranges" :key="r" :class="{ on: activeRange === r }" @click="activeRange = r">{{ r }}</button>
          </div>
        </div>
        <div class="rh-revenue-head">
          <div class="rh-revenue-sub">月度销售额</div>
          <div class="rh-revenue-amount"><span class="rh-unit">¥</span>15,000</div>
        </div>
        <!-- ECharts 柱状图 -->
        <div ref="chartRef" class="rh-echarts-container" />
      </div>

      <!-- 促销卡 -->
      <div class="rh-promo">
        <div class="rh-promo-tag">NEW</div>
        <h3 class="rh-promo-title">新版多租户管理已上线！</h3>
        <p class="rh-promo-desc">支持租户默认套餐配置、白名单批量分发，让企业级权限管理更轻盈、更高效。</p>
        <button class="rh-promo-btn">
          立即体验
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        </button>
      </div>
    </section>

    <!-- 底部行：最近动态 + 门店排行 -->
    <section class="rh-bot-row">
      <!-- 最近动态 -->
      <div class="rh-card">
        <div class="rh-card-header">
          <div class="rh-card-title">最近动态</div>
        </div>
        <div class="rh-feed">
          <div v-for="item in feedItems" :key="item.id" class="rh-feed-item">
            <div class="rh-feed-avatar" :class="item.avatarClass">{{ item.avatarText }}</div>
            <div>
              <div class="rh-feed-badge" :class="item.badgeClass">
                <svg v-if="item.badgeType === 'check'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <svg v-else-if="item.badgeType === 'warn'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                {{ item.badgeLabel }}
              </div>
              <!-- eslint-disable-next-line vue/no-v-html -->
              <div class="rh-feed-body" v-html="item.body" />
              <div class="rh-feed-time">{{ item.time }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 门店销售排行榜 -->
      <div class="rh-card">
        <div class="rh-card-header">
          <div class="rh-card-title">门店销售排行榜</div>
          <div class="rh-range" style="margin-left: auto">
            <button v-for="r in rankRanges" :key="r" :class="{ on: activeRankRange === r }" @click="activeRankRange = r">{{ r }}</button>
          </div>
        </div>
        <table class="rh-table">
          <thead>
            <tr>
              <th>No</th>
              <th>门店</th>
              <th>负责人</th>
              <th style="text-align: right">金额</th>
              <th style="text-align: right">状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rankRows" :key="row.rank">
              <td class="rh-rank-num">
                <span class="rh-rank-pill" :class="`r${row.rank}`">{{ row.rank }}</span>
              </td>
              <td><b>{{ row.store }}</b></td>
              <td>{{ row.owner }}</td>
              <td style="text-align: right">{{ row.amount }}</td>
              <td style="text-align: right">
                <span class="rh-status" :class="row.status">{{ row.statusLabel }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted, watch, defineComponent, h } from 'vue';
import echarts from '@/utils/lib/echarts';

// TODO: 占位数据，待接真实接口
const activeTab = ref('销售额');
const chartTabs = ['销售额', '销售趋势'];
const activeRange = ref('本月');
const ranges = ['今日', '本周', '本月', '本年'];
const activeRankRange = ref('本月');
const rankRanges = ['本月', '上月'];

// ---- 指标图标 (内联 SVG 组件) ----
const IconSales = defineComponent({
  render: () =>
    h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
      h('circle', { cx: '12', cy: '12', r: '10' }),
      h('path', { d: 'M12 6v12' }),
      h('path', { d: 'M16 10H9.5a2.5 2.5 0 0 0 0 5H14a2.5 2.5 0 0 1 0 5H7' }),
    ]),
});
const IconOrder = defineComponent({
  render: () =>
    h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
      h('path', { d: 'M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z' }),
      h('line', { x1: '3', y1: '6', x2: '21', y2: '6' }),
      h('path', { d: 'M16 10a4 4 0 0 1-8 0' }),
    ]),
});
const IconPay = defineComponent({
  render: () =>
    h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
      h('rect', { x: '1', y: '4', width: '22', height: '16', rx: '2', ry: '2' }),
      h('line', { x1: '1', y1: '10', x2: '23', y2: '10' }),
    ]),
});
const IconCampaign = defineComponent({
  render: () =>
    h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
      h('path', { d: 'M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z' }),
    ]),
});

// TODO: 占位数据，待接真实接口
const statCards = [
  { label: '总销售额', value: '¥126,560', delta: '12.00%', trend: 'up', icon: IconSales, chipBg: '#FFE4D6', chipFg: '#EA580C' },
  { label: '订单量', value: '8,846', delta: '8.20%', trend: 'up', icon: IconOrder, chipBg: '#D6F5E3', chipFg: '#059669' },
  { label: '支付笔数', value: '6,560', delta: '2.10%', trend: 'down', icon: IconPay, chipBg: '#DCE8FF', chipFg: '#1D4ED8' },
  { label: '运营活动效果', value: '78%', delta: '1.00%', trend: 'up', icon: IconCampaign, chipBg: '#FFE0EC', chipFg: '#DB2777' },
];

// TODO: 占位数据，待接真实接口
const monthlyData = [5400, 8100, 6150, 9750, 7200, 15000, 9000, 10800, 12000, 8250, 7500, 10200];
const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];

// TODO: 占位数据，待接真实接口
const feedItems = [
  { id: 1, avatarClass: '', avatarText: 'FG', badgeType: 'check', badgeClass: 'badge-new', badgeLabel: '新订单', body: '<b>张明远</b> 创建了订单 <b>PO-4491C</b>', time: '刚刚' },
  { id: 2, avatarClass: 'a2', avatarText: '!', badgeType: 'warn', badgeClass: 'badge-remind', badgeLabel: '待跟进', body: '订单 <b>JL-3432B</b> 已发送催办提醒至 <b>白鹭客户</b>', time: '今天 12:26' },
  { id: 3, avatarClass: 'a3', avatarText: 'L', badgeType: 'check', badgeClass: 'badge-done', badgeLabel: '已完成', body: '<b>李文静</b> 完成了租户 <b>东海贸易</b> 的套餐分配', time: '昨天 18:02' },
];

// TODO: 占位数据，待接真实接口
const rankRows = [
  { rank: 1, store: '白鹭 1 号店', owner: '张明远', amount: '¥1,234.56', status: 'paid', statusLabel: '已结算' },
  { rank: 2, store: '白鹭 2 号店', owner: '李文静', amount: '¥1,134.56', status: 'paid', statusLabel: '已结算' },
  { rank: 3, store: '白鹭 3 号店', owner: '赵蕊', amount: '¥1,034.56', status: 'pending', statusLabel: '待结算' },
  { rank: 4, store: '白鹭 4 号店', owner: '陈帆', amount: '¥934.56', status: 'paid', statusLabel: '已结算' },
  { rank: 5, store: '白鹭 5 号店', owner: '吴桐', amount: '¥834.56', status: 'overdue', statusLabel: '已逾期' },
  { rank: 6, store: '白鹭 6 号店', owner: '韩立', amount: '¥734.56', status: 'paid', statusLabel: '已结算' },
  { rank: 7, store: '白鹭 7 号店', owner: '苏小棠', amount: '¥634.56', status: 'pending', statusLabel: '待结算' },
];

// ---- ECharts ----
const chartRef = ref<HTMLDivElement | null>(null);
let chartInstance: ReturnType<typeof echarts.init> | null = null;

function buildChartOption() {
  return {
    grid: { top: 10, bottom: 30, left: 8, right: 8, containLabel: false },
    xAxis: {
      type: 'category',
      data: months,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { fontSize: 11, color: '#64748b' },
    },
    yAxis: { show: false },
    series: [
      {
        type: 'bar',
        data: monthlyData.map((v, i) => ({
          value: v,
          itemStyle: {
            color: i === 5 ? '#5b6cff' : '#eef1f6',
            borderRadius: [6, 6, 2, 2],
          },
          emphasis: {
            itemStyle: { color: '#dde2ff' },
          },
        })),
        barMaxWidth: 28,
        emphasis: { disabled: false },
      },
    ],
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'none' },
      backgroundColor: '#0f172a',
      borderColor: 'transparent',
      textStyle: { color: '#fff', fontSize: 11.5, fontWeight: 600 },
      formatter: (params: any[]) => `¥${params[0].value.toLocaleString()}`,
    },
  };
}

function initChart() {
  if (!chartRef.value) return;
  chartInstance = echarts.init(chartRef.value);
  chartInstance.setOption(buildChartOption());
}

function resizeChart() {
  chartInstance?.resize();
}

onMounted(() => {
  initChart();
  window.addEventListener('resize', resizeChart);
});

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart);
  chartInstance?.dispose();
  chartInstance = null;
});

watch(activeTab, () => {
  // TODO: 切换销售额/销售趋势后拉取对应数据并刷新图表
});
</script>

<style scoped lang="less">
.rh-dashboard {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-width: 0;
  padding: 16px;
}

/* ---- 指标卡 ---- */
.rh-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.rh-stat-card {
  background: var(--surface);
  border-radius: var(--radius-card);
  padding: 18px 20px;
  box-shadow: var(--shadow-card);
  display: flex;
  align-items: center;
  gap: 14px;
}
.rh-stat-chip {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.rh-chip-icon {
  width: 21px;
  height: 21px;
}
.rh-stat-body {
  min-width: 0;
  flex: 1;
}
.rh-stat-label {
  font-size: 12.5px;
  color: var(--ink-500);
  margin-bottom: 4px;
}
.rh-stat-value-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}
.rh-stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--ink-900);
  letter-spacing: -0.3px;
  font-variant-numeric: tabular-nums;
}
.rh-delta {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  white-space: nowrap;

  svg {
    width: 10px;
    height: 10px;
  }

  &.up {
    color: var(--good);
    background: var(--good-bg);
  }
  &.down {
    color: var(--bad);
    background: var(--bad-bg);
  }
}

/* ---- 中部行 ---- */
.rh-mid-row {
  display: grid;
  grid-template-columns: 1.7fr 1fr;
  gap: 16px;
}

/* ---- 通用卡片 ---- */
.rh-card {
  background: var(--surface);
  border-radius: var(--radius-card);
  padding: 20px 22px;
  box-shadow: var(--shadow-card);
}
.rh-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}
.rh-card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-900);
}

/* ---- Switcher ---- */
.rh-switcher {
  display: inline-flex;
  padding: 3px;
  background: var(--surface-2);
  border-radius: 999px;
  gap: 2px;

  button {
    border: 0;
    background: transparent;
    padding: 6px 14px;
    font-size: 12.5px;
    font-weight: 500;
    color: var(--ink-500);
    border-radius: 999px;
    cursor: pointer;
    font-family: inherit;
    transition: background-color var(--fast), color var(--fast);

    &.on {
      background: var(--surface);
      color: var(--accent);
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
      font-weight: 600;
    }
  }
}

/* ---- Range ---- */
.rh-range {
  display: inline-flex;
  gap: 4px;

  button {
    border: 0;
    background: transparent;
    padding: 6px 10px;
    font-size: 12px;
    color: var(--ink-500);
    border-radius: 7px;
    cursor: pointer;
    font-family: inherit;

    &:hover {
      background: var(--surface-2);
      color: var(--ink-700);
    }
    &.on {
      background: var(--accent-50);
      color: var(--accent);
      font-weight: 600;
    }
  }
}

/* ---- Revenue head ---- */
.rh-revenue-head {
  margin: 16px 0 6px;
}
.rh-revenue-sub {
  color: var(--ink-500);
  font-size: 12.5px;
  margin-bottom: 4px;
}
.rh-revenue-amount {
  font-size: 28px;
  font-weight: 800;
  color: var(--ink-900);
  letter-spacing: -0.5px;
  font-variant-numeric: tabular-nums;
}
.rh-unit {
  color: var(--ink-500);
  font-weight: 500;
  font-size: 16px;
  margin-right: 4px;
}

/* ---- ECharts container ---- */
.rh-echarts-container {
  margin-top: 18px;
  height: 210px;
  width: 100%;
}

/* ---- 促销卡 ---- */
.rh-promo {
  background: radial-gradient(circle at 110% 110%, rgba(255, 255, 255, 0.14), transparent 50%),
    linear-gradient(135deg, #3577f6 0%, var(--accent) 55%, #1b47b5 100%);
  color: #fff;
  border-radius: var(--radius-card);
  padding: 22px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 22px rgba(42, 107, 239, 0.22);
  display: flex;
  flex-direction: column;
  gap: 12px;

  &::before {
    content: '';
    position: absolute;
    width: 220px;
    height: 220px;
    right: -80px;
    bottom: -80px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
  }

  > * {
    position: relative;
    z-index: 1;
  }
}
.rh-promo-tag {
  display: inline-flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-size: 10.5px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  letter-spacing: 0.8px;
  width: max-content;
}
.rh-promo-title {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.3;
  margin: 0;
}
.rh-promo-desc {
  color: rgba(255, 255, 255, 0.85);
  font-size: 12.5px;
  line-height: 1.55;
  margin: 0;
}
.rh-promo-btn {
  margin-top: auto;
  background: #fff;
  color: var(--accent);
  padding: 10px 16px;
  border-radius: 999px;
  border: 0;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  width: max-content;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: inherit;

  svg {
    width: 13px;
    height: 13px;
  }
}

/* ---- 底部行 ---- */
.rh-bot-row {
  display: grid;
  grid-template-columns: 1fr 1.6fr;
  gap: 16px;
}

/* ---- Feed ---- */
.rh-feed {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 12px;
}
.rh-feed-item {
  display: flex;
  gap: 12px;
}
.rh-feed-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, #cbd5e1, #94a3b8);
  flex-shrink: 0;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 700;
  font-size: 12px;

  &.a2 {
    background: linear-gradient(135deg, #fcd34d, #f59e0b);
  }
  &.a3 {
    background: linear-gradient(135deg, #86efac, #10b981);
  }
}
.rh-feed-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 10.5px;
  font-weight: 600;
  margin-bottom: 4px;

  svg {
    width: 10px;
    height: 10px;
  }

  &.badge-new {
    background: var(--good-bg);
    color: var(--good);
  }
  &.badge-remind {
    background: var(--warn-bg);
    color: var(--warn);
  }
  &.badge-done {
    background: var(--accent-50);
    color: var(--accent);
  }
}
.rh-feed-body {
  font-size: 12.5px;
  color: var(--ink-700);
  line-height: 1.5;
  min-width: 0;

  :deep(b) {
    color: var(--ink-900);
    font-weight: 600;
  }
}
.rh-feed-time {
  font-size: 11px;
  color: var(--ink-400);
  margin-top: 3px;
}

/* ---- 排行榜表格 ---- */
.rh-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;

  thead th {
    font-size: 11.5px;
    color: var(--ink-500);
    font-weight: 600;
    text-align: left;
    padding: 10px 4px 12px;
    border-bottom: 1px solid var(--line);
  }

  tbody td {
    font-size: 12.5px;
    color: var(--ink-700);
    padding: 12px 4px;
    border-bottom: 1px solid var(--line);
  }

  tbody tr:last-child td {
    border-bottom: 0;
  }

  tbody tr:hover td {
    background: var(--surface-2);
  }
}
.rh-rank-num {
  width: 32px;
}
.rh-rank-pill {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: inline-grid;
  place-items: center;
  font-size: 11.5px;
  font-weight: 700;
  color: #fff;
  background: var(--ink-300);

  &.r1 {
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
  }
  &.r2 {
    background: linear-gradient(135deg, #a8b6cb, #64748b);
  }
  &.r3 {
    background: linear-gradient(135deg, #fb923c, #c2410c);
  }
}
.rh-status {
  display: inline-flex;
  align-items: center;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.3px;

  &.paid {
    background: var(--good-bg);
    color: var(--good);
  }
  &.overdue {
    background: var(--bad-bg);
    color: var(--bad);
  }
  &.pending {
    background: var(--warn-bg);
    color: var(--warn);
  }
}

/* ---- Responsive ---- */
@media (max-width: 1100px) {
  .rh-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 800px) {
  .rh-mid-row,
  .rh-bot-row {
    grid-template-columns: 1fr;
  }
  .rh-stats {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
