<template>
  <div class="bg-white border border-gray-200 rounded-xl p-6">
    <h3 class="text-base font-semibold text-[#111827] mb-4">{{ title }}</h3>
    <div v-if="hasData" ref="chartRef" class="w-full h-[300px]"></div>
    <div v-else class="flex flex-col items-center justify-center h-[300px] text-gray-400">
      <svg class="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <span class="text-sm">暂无数据</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  title: string
  dates: string[]
  values: number[]
}>()

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null
const hasData = ref(false)

function initChart() {
  if (!chartRef.value || !props.dates.length) return
  hasData.value = true

  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, bottom: 30, top: 20 },
    xAxis: {
      type: 'category',
      data: props.dates,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#9CA3AF', fontSize: 12 },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#F3F4F6' } },
      axisLabel: { color: '#9CA3AF', fontSize: 12 },
    },
    series: [{
      type: 'line',
      data: props.values,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: '#3B82F6', width: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(59, 130, 246, 0.15)' },
          { offset: 1, color: 'rgba(59, 130, 246, 0)' },
        ]),
      },
      itemStyle: { color: '#3B82F6' },
    }],
  })
}

function resize() {
  chartInstance?.resize()
}

watch(() => props.dates, () => {
  chartInstance?.dispose()
  chartInstance = null
  if (props.dates.length) initChart()
})

onMounted(() => {
  if (props.dates.length) initChart()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  chartInstance?.dispose()
  window.removeEventListener('resize', resize)
})
</script>
