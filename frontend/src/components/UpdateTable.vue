<template>
  <div class="bg-white border border-gray-200 rounded-xl p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-base font-semibold text-[#111827]">{{ title }}</h3>
      <a v-if="linkText" class="text-sm text-brand-500 hover:text-brand-600 cursor-pointer">{{ linkText }} →</a>
    </div>

    <!-- Empty state -->
    <div v-if="!items.length" class="flex flex-col items-center justify-center py-12 text-gray-400">
      <svg class="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <span class="text-sm">暂无数据</span>
    </div>

    <!-- Table -->
    <table v-else class="w-full">
      <thead>
        <tr class="border-b border-gray-100">
          <th
            v-for="col in columns"
            :key="col.key"
            class="text-left py-3 px-2 text-sm font-medium text-gray-600 bg-gray-50 first:rounded-l-lg last:rounded-r-lg"
            :style="col.width ? { width: col.width } : {}"
          >
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, i) in items"
          :key="i"
          class="border-b border-gray-50 hover:bg-gray-50 transition-colors"
        >
          <td
            v-for="col in columns"
            :key="col.key"
            class="py-3 px-2 text-sm text-gray-700"
          >
            <slot :name="`cell-${col.key}`" :row="row">
              {{ row[col.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  columns: { key: string; label: string; width?: string }[]
  items: Record<string, any>[]
  linkText?: string
}>()
</script>
