<template>
  <div>
    <div v-if="status !== 'idle'" style="margin-bottom: 8px; display: flex; align-items: center; gap: 8px">
      <el-tag v-if="status === 'running'" type="warning" effect="dark">运行中</el-tag>
      <el-tag v-else-if="status === 'success'" type="success" effect="dark">完成</el-tag>
      <el-tag v-else-if="status === 'error'" type="danger" effect="dark">错误</el-tag>
    </div>
    <div v-if="errorMessage" style="color: var(--pm-danger); margin-bottom: 8px; font-size: 13px; padding: 8px 12px; background: #FEF2F2; border-radius: 6px">
      <el-icon style="margin-right: 4px; vertical-align: middle"><WarningFilled /></el-icon>
      {{ errorMessage }}
    </div>
    <div
      v-if="output || status === 'running'"
      class="stream-output"
    >
      {{ output }}<span v-if="status === 'running'" class="cursor">▊</span>
    </div>
    <div v-if="usage && status === 'success'" class="stream-stats">
      <span>输入 {{ usage.prompt_tokens }} tokens</span>
      <span class="dot">·</span>
      <span>输出 {{ usage.completion_tokens }} tokens</span>
      <span class="dot">·</span>
      <span>{{ latency }}ms</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { WarningFilled } from '@element-plus/icons-vue'

const output = ref('')
const status = ref<'idle' | 'running' | 'success' | 'error'>('idle')
const errorMessage = ref('')
const usage = ref<{ prompt_tokens: number; completion_tokens: number } | null>(null)
const latency = ref(0)

function reset() {
  output.value = ''
  status.value = 'running'
  errorMessage.value = ''
  usage.value = null
  latency.value = 0
}

function handleEvent(event: any) {
  if (event.type === 'token') {
    output.value += event.data
  } else if (event.type === 'done') {
    usage.value = event.usage
    latency.value = event.latency_ms
    status.value = 'success'
  } else if (event.type === 'error') {
    errorMessage.value = event.message
    status.value = 'error'
  }
}

// EventSource-based connection (for GET SSE endpoints)
function connect(es: EventSource) {
  reset()
  es.addEventListener('token', (e: MessageEvent) => {
    try { handleEvent(JSON.parse(e.data)) } catch {}
  })
  es.addEventListener('done', (e: MessageEvent) => {
    try { handleEvent(JSON.parse(e.data)) } catch {}
    es.close()
  })
  es.addEventListener('error', (e: MessageEvent) => {
    try { handleEvent(JSON.parse(e.data)) } catch {
      errorMessage.value = '连接中断'
      status.value = 'error'
    }
    es.close()
  })
  es.onerror = () => {
    if (status.value === 'running') {
      errorMessage.value = '连接中断'
      status.value = 'error'
    }
    es.close()
  }
}

function disconnect() {
  status.value = 'idle'
}

defineExpose({ connect, disconnect, reset, handleEvent })
</script>

<style scoped>
.stream-output {
  background: #1E293B;
  color: #E2E8F0;
  padding: 16px;
  border-radius: 8px;
  min-height: 80px;
  white-space: pre-wrap;
  font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
}

.cursor {
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.stream-stats {
  margin-top: 8px;
  color: var(--pm-text-muted);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  color: var(--pm-border);
}
</style>
