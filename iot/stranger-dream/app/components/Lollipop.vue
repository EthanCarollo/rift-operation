<template>
    <div class="lollipop" :style="lollipopStyle">
        <!-- Stick -->
        <div class="lollipop-stick"></div>
        <!-- Spiral candy head -->
        <div class="lollipop-head">
            <svg viewBox="0 0 100 100" class="w-full h-full">
                <circle cx="50" cy="50" r="45" :fill="bgColor" />
                <path
                    d="M50,5 A45,45 0 0,1 95,50 A40,40 0 0,0 50,10 A35,35 0 0,1 85,50 A30,30 0 0,0 50,20 A25,25 0 0,1 75,50 A20,20 0 0,0 50,30 A15,15 0 0,1 65,50 A10,10 0 0,0 50,40 A5,5 0 0,1 55,50"
                    :stroke="spiralColor" stroke-width="8" fill="none" stroke-linecap="round" />
            </svg>
        </div>
    </div>
</template>

<script setup lang="ts">
interface Props {
    color?: 'yellow' | 'green' | 'rose'
    size?: 'sm' | 'md' | 'lg'
    rotation?: number
}

const props = withDefaults(defineProps<Props>(), {
    color: 'yellow',
    size: 'md',
    rotation: 0
})

const colorMap = {
    yellow: { bg: '#FFFF00', spiral: '#FF00CF' },
    green: { bg: '#00FFC4', spiral: '#FF00CF' },
    rose: { bg: '#FF00CF', spiral: '#FFFF00' }
}

const sizeMap = {
    sm: { head: '60px', stick: '80px' },
    md: { head: '100px', stick: '120px' },
    lg: { head: '140px', stick: '160px' }
}

const bgColor = computed(() => colorMap[props.color].bg)
const spiralColor = computed(() => colorMap[props.color].spiral)

const lollipopStyle = computed(() => ({
    '--head-size': sizeMap[props.size].head,
    '--stick-height': sizeMap[props.size].stick,
    transform: `rotate(${props.rotation}deg)`
}))
</script>

<style scoped>
.lollipop {
    display: flex;
    flex-direction: column;
    align-items: center;
    transform-origin: center bottom;
}

.lollipop-head {
    width: var(--head-size, 100px);
    height: var(--head-size, 100px);
    border-radius: 50%;
    overflow: hidden;
    position: relative;
    z-index: 2;
}

.lollipop-stick {
    width: 8px;
    height: var(--stick-height, 120px);
    background: linear-gradient(to bottom, #150059, #2a0080);
    border-radius: 4px;
    margin-top: -10px;
    z-index: 1;
}
</style>
