<template>
  <div>
    <!-- Stats -->
    <div class="flex flex-wrap gap-6 mb-6">
      <StatCard :value="promptCount" label="提示词总数" trend="100%" />
      <StatCard :value="batchCount" label="测试批次" />
      <StatCard :value="callCount" label="今日调用次数" />
    </div>

    <!-- Chart -->
    <div class="mb-6">
      <ChartCard title="提示词调用趋势" :dates="chartDates" :values="chartValues" />
    </div>

    <!-- Recent updates -->
    <UpdateTable
      title="最近更新"
      linkText="查看全部"
      :columns="[
        { key: 'title', label: '标题', width: 'auto' },
        { key: 'updated_at', label: '更新时间', width: '180px' },
        { key: 'status', label: '状态', width: '100px' },
      ]"
      :items="recentPrompts"
    >
      <template #cell-status="{ row }">
        <span
          class="inline-flex items-center px-2 py-[2px] rounded-full text-xs font-medium"
          :class="row.status === 'success' ? 'bg-green-50 text-green-700' : 'bg-gray-50 text-gray-500'"
        >
          {{ row.status || '草稿' }}
        </span>
      </template>
    </UpdateTable>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchPrompts } from '@/api/prompts'
import { fetchBatchTests } from '@/api/tests'
import StatCard from '@/components/StatCard.vue'
import ChartCard from '@/components/ChartCard.vue'
import UpdateTable from '@/components/UpdateTable.vue'

const promptCount = ref(0)
const batchCount = ref(0)
const callCount = ref(0)
const recentPrompts = ref<any[]>([])
const chartDates = ref<string[]>([])
const chartValues = ref<number[]>([])

function generateChartDates(): [string[], number[]] {
  const dates: string[] = []
  const values: number[] = []
  const now = new Date()
  for (let i = 6; i >= 0; i--) {
    const d = new Date(now)
    d.setDate(d.getDate() - i)
    dates.push(`${d.getMonth() + 1}-${d.getDate()}`)
    values.push(0)
  }
  return [dates, values]
}

onMounted(async () => {
  const [dates, values] = generateChartDates()
  chartDates.value = dates
  chartValues.value = values

  try {
    const [promptsRes, batches] = await Promise.all([
      fetchPrompts({ page: 1, page_size: 10, sort_by: 'updated_at', sort_order: 'desc' }),
      fetchBatchTests(),
    ])
    recentPrompts.value = promptsRes.items.map((p: any) => ({
      ...p,
      status: '草稿',
      updated_at: new Date(p.updated_at).toLocaleString('zh-CN'),
    }))
    promptCount.value = promptsRes.total
    batchCount.value = batches.length
  } catch {
    // silent
  }
})
</script>
