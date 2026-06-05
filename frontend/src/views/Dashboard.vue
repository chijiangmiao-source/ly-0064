<template>
  <div class="dashboard">
    <n-row :gutter="16" class="mb-4">
      <n-col :span="6">
        <n-card hoverable>
          <div class="stat-card">
            <div class="stat-icon warning">
              <n-icon size="28"><alert-outline /></n-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">临期原料</div>
              <div class="stat-value">{{ stats?.expiring_soon_count || 0 }}</div>
            </div>
          </div>
        </n-card>
      </n-col>
      <n-col :span="6">
        <n-card hoverable>
          <div class="stat-card">
            <div class="stat-icon error">
              <n-icon size="28"><close-circle-outline /></n-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">已过期</div>
              <div class="stat-value">{{ stats?.expired_count || 0 }}</div>
            </div>
          </div>
        </n-card>
      </n-col>
      <n-col :span="6">
        <n-card hoverable>
          <div class="stat-card">
            <div class="stat-icon info">
              <n-icon size="28"><cube-outline /></n-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">原料总数</div>
              <div class="stat-value">{{ stats?.total_materials || 0 }}</div>
            </div>
          </div>
        </n-card>
      </n-col>
      <n-col :span="6">
        <n-card hoverable>
          <div class="stat-card">
            <div class="stat-icon success">
              <n-icon size="28"><archive-outline /></n-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">总库存</div>
              <div class="stat-value">{{ stats?.total_stock || 0 }}</div>
            </div>
          </div>
        </n-card>
      </n-col>
    </n-row>

    <n-row :gutter="16" class="mb-4">
      <n-col :span="12">
        <n-card title="近7天领用趋势" class="h-full">
          <div ref="trendChartRef" style="height: 320px;"></div>
        </n-card>
      </n-col>
      <n-col :span="12">
        <n-card title="领用最多原料排行" class="h-full">
          <n-data-table
            :columns="usageRankingColumns"
            :data="stats?.usage_ranking || []"
            :bordered="false"
            :pagination="false"
            size="small"
          />
        </n-card>
      </n-col>
    </n-row>

    <n-row :gutter="16" class="mb-4">
      <n-col :span="12">
        <n-card title="近7天调拨趋势" class="h-full">
          <div ref="transferTrendChartRef" style="height: 320px;"></div>
        </n-card>
      </n-col>
      <n-col :span="12">
        <n-card title="调拨最多原料排行" class="h-full">
          <n-data-table
            :columns="transferRankingColumns"
            :data="stats?.transfer_ranking || []"
            :bordered="false"
            :pagination="false"
            size="small"
          />
        </n-card>
      </n-col>
    </n-row>

    <n-row :gutter="16" class="mb-4">
      <n-col :span="12">
        <n-card title="近7天退货趋势" class="h-full">
          <div ref="returnTrendChartRef" style="height: 320px;"></div>
        </n-card>
      </n-col>
      <n-col :span="12">
        <n-card title="退货最多原料排行" class="h-full">
          <n-data-table
            :columns="returnRankingColumns"
            :data="stats?.return_ranking || []"
            :bordered="false"
            :pagination="false"
            size="small"
          />
        </n-card>
      </n-col>
    </n-row>

    <n-row :gutter="16">
      <n-col :span="12">
        <n-card title="报损排行" class="h-full">
          <n-data-table
            :columns="rankingColumns"
            :data="stats?.damage_ranking || []"
            :bordered="false"
            :pagination="false"
            size="small"
          />
        </n-card>
      </n-col>
      <n-col :span="12">
        <n-card title="分类库存分布">
          <div ref="chartRef" style="height: 320px;"></div>
        </n-card>
      </n-col>
    </n-row>

    <n-row :gutter="16" class="mt-4">
      <n-col :span="24">
        <n-card title="效期预警">
          <n-data-table
            :columns="warningColumns"
            :data="expiryWarnings"
            :bordered="false"
            size="small"
          />
        </n-card>
      </n-col>
    </n-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h, nextTick } from 'vue'
import { useMessage, NTag } from 'naive-ui'
import {
  AlertOutline,
  CloseCircleOutline,
  CubeOutline,
  ArchiveOutline
} from '@vicons/ionicons5'
import * as echarts from 'echarts'
import api from '@/utils/api'

interface DashboardStats {
  expiring_soon_count: number
  expired_count: number
  total_materials: number
  total_stock: number
  damage_ranking: DamageRanking[]
  category_stock: CategoryStock[]
  usage_trend: UsageTrend[]
  usage_ranking: UsageRanking[]
  transfer_trend: TransferTrend[]
  transfer_ranking: TransferRanking[]
  return_trend: ReturnTrend[]
  return_ranking: ReturnRanking[]
}

interface DamageRanking {
  material_id: number
  material_name: string
  material_code: string
  total_damage: number
  damage_count: number
}

interface UsageRanking {
  material_id: number
  material_name: string
  material_code: string
  total_quantity: number
  usage_count: number
}

interface UsageTrend {
  date: string
  total_quantity: number
  record_count: number
}

interface TransferTrend {
  date: string
  total_quantity: number
  record_count: number
}

interface TransferRanking {
  material_id: number
  material_name: string
  material_code: string
  total_quantity: number
  transfer_count: number
}

interface ReturnTrend {
  date: string
  total_quantity: number
  record_count: number
}

interface ReturnRanking {
  material_id: number
  material_name: string
  material_code: string
  total_quantity: number
  return_count: number
}

interface CategoryStock {
  category_id: number
  category_name: string
  total_stock: number
  material_count: number
}

interface ExpiryWarning {
  id: number
  code: string
  name: string
  expiry_date: string
  days_remaining: number
  current_status: string
}

const message = useMessage()
const stats = ref<DashboardStats | null>(null)
const expiryWarnings = ref<ExpiryWarning[]>([])
const chartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)
const transferTrendChartRef = ref<HTMLElement | null>(null)
const returnTrendChartRef = ref<HTMLElement | null>(null)

const rankingColumns = [
  { title: '排名', key: 'rank', width: 80, render: (_: any, index: number) => index + 1 },
  { title: '原料名称', key: 'material_name' },
  { title: '原料编号', key: 'material_code', width: 120 },
  { title: '报损总量', key: 'total_damage', width: 120 },
  { title: '报损次数', key: 'damage_count', width: 120 }
]

const usageRankingColumns = [
  { title: '排名', key: 'rank', width: 80, render: (_: any, index: number) => index + 1 },
  { title: '原料名称', key: 'material_name' },
  { title: '原料编号', key: 'material_code', width: 120 },
  { title: '领用总量', key: 'total_quantity', width: 120 },
  { title: '领用次数', key: 'usage_count', width: 120 }
]

const transferRankingColumns = [
  { title: '排名', key: 'rank', width: 80, render: (_: any, index: number) => index + 1 },
  { title: '原料名称', key: 'material_name' },
  { title: '原料编号', key: 'material_code', width: 120 },
  { title: '调拨总量', key: 'total_quantity', width: 120 },
  { title: '调拨次数', key: 'transfer_count', width: 120 }
]

const returnRankingColumns = [
  { title: '排名', key: 'rank', width: 80, render: (_: any, index: number) => index + 1 },
  { title: '原料名称', key: 'material_name' },
  { title: '原料编号', key: 'material_code', width: 120 },
  { title: '退货总量', key: 'total_quantity', width: 120 },
  { title: '退货次数', key: 'return_count', width: 120 }
]

const warningColumns = [
  { title: '原料编号', key: 'code', width: 120 },
  { title: '原料名称', key: 'name' },
  { title: '失效日期', key: 'expiry_date', width: 120 },
  {
    title: '剩余天数',
    key: 'days_remaining',
    width: 120,
    render: (row: ExpiryWarning) => {
      const type = row.days_remaining <= 0 ? 'error' : row.days_remaining <= 3 ? 'warning' : 'info'
      return h(NTag, { type }, { default: () => row.days_remaining <= 0 ? '已过期' : `${row.days_remaining}天` })
    }
  },
  {
    title: '状态',
    key: 'current_status',
    width: 100,
    render: (row: ExpiryWarning) => {
      const statusMap: Record<string, string> = {
        expired: 'error',
        opened: 'warning',
        in_stock: 'success'
      }
      const labelMap: Record<string, string> = {
        expired: '已过期',
        opened: '已开封',
        in_stock: '在库'
      }
      return h(NTag, { type: statusMap[row.current_status] || 'default' }, {
        default: () => labelMap[row.current_status] || row.current_status
      })
    }
  }
]

async function fetchStats() {
  try {
    const response = await api.get('/dashboard/stats')
    stats.value = response.data
    await nextTick()
    initChart()
    initTrendChart()
    initTransferTrendChart()
    initReturnTrendChart()
  } catch (error) {
    message.error('获取统计数据失败')
  }
}

async function fetchExpiryWarnings() {
  try {
    const response = await api.get('/dashboard/expiry-warnings')
    expiryWarnings.value = response.data
  } catch (error) {
    message.error('获取效期预警失败')
  }
}

function initChart() {
  if (!chartRef.value || !stats.value) return

  const chart = echarts.init(chartRef.value)
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      bottom: '5%',
      left: 'center'
    },
    series: [
      {
        name: '库存分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: stats.value.category_stock.map((item: CategoryStock) => ({
          value: item.total_stock,
          name: item.category_name
        }))
      }
    ]
  }
  chart.setOption(option)
}

function initTrendChart() {
  if (!trendChartRef.value || !stats.value) return

  const chart = echarts.init(trendChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: stats.value.usage_trend.map((item: UsageTrend) => item.date.slice(5))
    },
    yAxis: [
      {
        type: 'value',
        name: '领用数量',
        position: 'left'
      },
      {
        type: 'value',
        name: '领用次数',
        position: 'right'
      }
    ],
    series: [
      {
        name: '领用数量',
        type: 'line',
        smooth: true,
        itemStyle: {
          color: '#58a6ff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(88, 166, 255, 0.3)' },
            { offset: 1, color: 'rgba(88, 166, 255, 0.05)' }
          ])
        },
        data: stats.value.usage_trend.map((item: UsageTrend) => item.total_quantity)
      },
      {
        name: '领用次数',
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        itemStyle: {
          color: '#4cb782'
        },
        data: stats.value.usage_trend.map((item: UsageTrend) => item.record_count)
      }
    ]
  }
  chart.setOption(option)
}

function initTransferTrendChart() {
  if (!transferTrendChartRef.value || !stats.value) return

  const chart = echarts.init(transferTrendChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: stats.value.transfer_trend.map((item: TransferTrend) => item.date.slice(5))
    },
    yAxis: [
      {
        type: 'value',
        name: '调拨数量',
        position: 'left'
      },
      {
        type: 'value',
        name: '调拨次数',
        position: 'right'
      }
    ],
    series: [
      {
        name: '调拨数量',
        type: 'line',
        smooth: true,
        itemStyle: {
          color: '#f0a020'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(240, 160, 32, 0.3)' },
            { offset: 1, color: 'rgba(240, 160, 32, 0.05)' }
          ])
        },
        data: stats.value.transfer_trend.map((item: TransferTrend) => item.total_quantity)
      },
      {
        name: '调拨次数',
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        itemStyle: {
          color: '#a855f7'
        },
        data: stats.value.transfer_trend.map((item: TransferTrend) => item.record_count)
      }
    ]
  }
  chart.setOption(option)
}

function initReturnTrendChart() {
  if (!returnTrendChartRef.value || !stats.value) return

  const chart = echarts.init(returnTrendChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: stats.value.return_trend.map((item: ReturnTrend) => item.date.slice(5))
    },
    yAxis: [
      {
        type: 'value',
        name: '退货数量',
        position: 'left'
      },
      {
        type: 'value',
        name: '退货次数',
        position: 'right'
      }
    ],
    series: [
      {
        name: '退货数量',
        type: 'line',
        smooth: true,
        itemStyle: {
          color: '#e76565'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(231, 101, 101, 0.3)' },
            { offset: 1, color: 'rgba(231, 101, 101, 0.05)' }
          ])
        },
        data: stats.value.return_trend.map((item: ReturnTrend) => item.total_quantity)
      },
      {
        name: '退货次数',
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        itemStyle: {
          color: '#f59e0b'
        },
        data: stats.value.return_trend.map((item: ReturnTrend) => item.record_count)
      }
    ]
  }
  chart.setOption(option)
}

onMounted(() => {
  fetchStats()
  fetchExpiryWarnings()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.warning {
  background: #fff3e0;
  color: #ed956e;
}

.stat-icon.error {
  background: #ffe7e7;
  color: #e76565;
}

.stat-icon.info {
  background: #e5f0ff;
  color: #58a6ff;
}

.stat-icon.success {
  background: #e5fff0;
  color: #4cb782;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.h-full {
  height: 100%;
}

.mb-4 {
  margin-bottom: 16px;
}

.mt-4 {
  margin-top: 16px;
}
</style>
