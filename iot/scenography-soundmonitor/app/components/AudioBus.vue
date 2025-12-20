<template>
    <div class="h-full flex flex-col bg-bg-sec border-r border-border min-w-[80px] w-24 relative group select-none">
        <!-- Bus Header -->
        <div
            class="h-8 bg-bg-main border-b border-border flex items-center justify-center cursor-pointer hover:bg-card-hover transition-colors">
            <span class="text-[10px] font-bold text-text-sec group-hover:text-text-main truncate px-1">
                {{ busName }}
            </span>
        </div>

        <!-- FX/Inserts Placeholder -->
        <div class="flex-1 flex flex-col gap-[1px] bg-tri-state-bg p-[1px]">
            <div v-for="i in 4" :key="i" class="h-4 bg-tri-state-hover hover:bg-border cursor-pointer"></div>
        </div>

        <!-- Controls Area -->
        <div class="h-[280px] bg-bg-sec flex flex-col items-center pt-2 gap-2 border-t border-border">

            <!-- Pan Knob (Visual) -->
            <div class="w-8 h-8 rounded-full border border-border bg-bg-main relative flex items-center justify-center">
                <div class="w-[2px] h-3 bg-text-sec -translate-y-[2px]"></div>
            </div>

            <!-- Fader Section -->
            <div class="flex items-end justify-center gap-1 h-40 w-full px-2">

                <!-- Meter L -->
                <div
                    class="w-1.5 h-full bg-tri-state-bg flex flex-col-reverse overflow-hidden relative border border-border/50">
                    <div class="w-full bg-gradient-to-t from-green-500 via-yellow-500 to-red-500 opacity-80"
                        :style="{ height: meterLevel + '%' }"></div>
                </div>

                <!-- Fader Track -->
                <div class="w-6 h-full bg-tri-state-bg relative mx-1 py-2 border border-border/50 rounded-sm">
                    <div class="absolute inset-x-0 h-[80%] bg-border/30 mx-2 top-[10%] rounded-full"></div>

                    <!-- Fader Handle -->
                    <div class="absolute w-full h-8 bg-bg-main border-y border-border shadow-md cursor-grab active:cursor-grabbing hover:bg-white transition-colors flex items-center justify-center z-10"
                        :style="{ bottom: faderPosition + '%' }" @mousedown.prevent="startDrag">
                        <div class="w-full h-[1px] bg-text-main opacity-50"></div>
                    </div>
                </div>

                <!-- Meter R -->
                <div
                    class="w-1.5 h-full bg-tri-state-bg flex flex-col-reverse overflow-hidden relative border border-border/50">
                    <div class="w-full bg-gradient-to-t from-green-500 via-yellow-500 to-red-500 opacity-80"
                        :style="{ height: meterLevel * 0.9 + '%' }"></div>
                </div>

            </div>

            <!-- Mute/Solo -->
            <div class="flex gap-1 w-full px-2 justify-center">
                <button
                    :class="['w-4 h-4 text-[8px] font-bold border flex items-center justify-center transition-colors', isMuted ? 'bg-red-500 text-white border-red-600' : 'bg-bg-main text-text-sec border-border hover:bg-card-hover']"
                    @click="isMuted = !isMuted">M</button>
                <button
                    :class="['w-4 h-4 text-[8px] font-bold border flex items-center justify-center transition-colors', isSolo ? 'bg-yellow-400 text-black border-yellow-500' : 'bg-bg-main text-text-sec border-border hover:bg-card-hover']"
                    @click="isSolo = !isSolo">S</button>
            </div>

        </div>

        <!-- Device Selector (Bottom) -->
        <div class="h-14 bg-bg-main border-t border-border p-1 flex flex-col justify-center">
            <label class="text-[8px] text-text-sec uppercase text-center mb-1 font-bold">Output</label>
            <select
                class="w-full h-5 text-[9px] bg-bg-sec text-text-main border border-border outline-none hover:border-border-focus focus:border-accent cursor-pointer">
                <option value="" disabled selected>-- Out --</option>
                <option v-for="dev in devices" :key="dev.id" :value="dev.id">{{ dev.name }}</option>
            </select>
        </div>

    </div>
</template>

<script setup lang="ts">
const props = defineProps<{
    busName: string;
    busId: number;
    devices: { id: string; name: string }[];
}>();

const faderPosition = ref(75); // 0-100%
const meterLevel = ref(0);
const isMuted = ref(false);
const isSolo = ref(false);

// Simple interaction for drag
const isDragging = ref(false);

const startDrag = (e: MouseEvent) => {
    isDragging.value = true;
    window.addEventListener('mousemove', onDrag);
    window.addEventListener('mouseup', stopDrag);
};

const onDrag = (e: MouseEvent) => {
    if (!isDragging.value) return;
    // Simplified vertical drag simulation
    const movement = e.movementY;
    faderPosition.value = Math.max(0, Math.min(90, faderPosition.value - movement)); // Invert Y
};

const stopDrag = () => {
    isDragging.value = false;
    window.removeEventListener('mousemove', onDrag);
    window.removeEventListener('mouseup', stopDrag);
};

// Fake meter animation
onMounted(() => {
    setInterval(() => {
        meterLevel.value = Math.random() * (faderPosition.value + 10);
    }, 100);
});
</script>

<style scoped>
/* Optional specific overrides if needed */
</style>
