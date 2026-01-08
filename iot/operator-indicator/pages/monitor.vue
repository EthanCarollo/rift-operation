<script setup lang="ts">
const { data: status, refresh, error } = await useFetch('/api/status')

onMounted(() => {
  const interval = setInterval(() => {
    refresh()
  }, 1000)

  onUnmounted(() => {
    clearInterval(interval)
  })
})

const sections = computed(() => {
  if (!status.value) return []

  return [
    {
      title: 'System Control',
      items: [
        { label: 'Start System', value: status.value.start_system },
        { label: 'End System', value: status.value.end_system },
        { label: 'Reset System', value: status.value.reset_system },
        { label: 'Operator Start', value: status.value.operator_start_system },
      ]
    },
    {
      title: 'Rift & Operator',
      items: [
        { label: 'Rift Part Count', value: status.value.rift_part_count },
        { label: 'Close Rift Step 1', value: status.value.operator_launch_close_rift_step_1 },
        { label: 'Close Rift Step 2', value: status.value.operator_launch_close_rift_step_2 },
        { label: 'Close Rift Step 3', value: status.value.operator_launch_close_rift_step_3 },
      ]
    },
    {
      title: 'Stranger',
      items: [
        { label: 'State', value: status.value.stranger_state },
        { label: 'Recognized Name', value: status.value.stranger_recognized_name },
      ]
    },
    {
      title: 'Depth',
      items: [
        { label: 'State', value: status.value.depth_state },
        { label: 'NM Step 1 Success', value: status.value.depth_step_1_nightmare_sucess },
        { label: 'NM Step 2 Success', value: status.value.depth_step_2_nightmare_sucess },
        { label: 'NM Step 3 Success', value: status.value.depth_step_3_nightmare_sucess },
        { label: 'Dream Step 1 Success', value: status.value.depth_step_1_dream_sucess },
        { label: 'Dream Step 2 Success', value: status.value.depth_step_2_dream_sucess },
        { label: 'Dream Step 3 Success', value: status.value.depth_step_3_dream_sucess },
      ]
    },
    {
      title: 'Lost',
      items: [
        { label: 'State', value: status.value.lost_state },
        { label: 'Light Recognized', value: status.value.lost_drawing_light_recognized },
        { label: 'Cage on Monster', value: status.value.lost_cage_is_on_monster },
        { label: 'Light Triggered', value: status.value.lost_light_is_triggered },
      ]
    }
  ]
})

const formatValue = (val: any) => {
  if (val === null) return 'Waiting...'
  if (val === true) return 'Active'
  if (val === false) return 'Inactive'
  return val
}

const getStatusColor = (val: any) => {
  if (val === true) return 'text-green-400'
  if (val === false) return 'text-red-400'
  if (val === null) return 'text-gray-500'
  return 'text-white'
}
</script>

<template>
  <div class="min-h-screen bg-neutral-950 text-white p-8 font-sans">
    <div class="max-w-7xl mx-auto space-y-12">
      <header class="flex items-center justify-between border-b border-white/10 pb-6">
        <div>
          <h1 class="text-3xl font-light tracking-tight text-white mb-2">System Monitor</h1>
          <p class="text-neutral-400 text-sm">Real-time status of all subsystem components.</p>
        </div>
        <div class="flex items-center gap-2 text-xs uppercase tracking-wider">
           <div class="w-2 h-2 rounded-full animate-pulse" :class="status ? 'bg-green-500' : 'bg-red-500'"></div>
           {{ status ? 'Connected' : 'Disconnected' }}
        </div>
      </header>

      <div v-if="error" class="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-lg">
        Failed to load system status. Is the server running?
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="section in sections"
          :key="section.title"
          class="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-sm hover:bg-white/10 transition-colors duration-300"
        >
          <h2 class="text-lg font-medium text-white/90 mb-6 border-b border-white/5 pb-2">{{ section.title }}</h2>
          <div class="space-y-4">
            <div v-for="item in section.items" :key="item.label" class="flex items-center justify-between group">
              <span class="text-sm text-neutral-400 group-hover:text-neutral-200 transition-colors">{{ item.label }}</span>
              <span class="font-mono text-sm font-medium" :class="getStatusColor(item.value)">
                {{ formatValue(item.value) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
