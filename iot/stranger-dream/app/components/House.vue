<template>
    <div class="house" :style="houseStyle">
        <!-- Roof -->
        <div class="house-roof">
            <svg viewBox="0 0 100 60" class="w-full h-full">
                <polygon points="50,0 100,60 0,60" fill="#FFFF00" stroke="#FF00CF" stroke-width="4" />
                <!-- Window in roof -->
                <circle cx="50" cy="35" r="12" fill="#00FFC4" />
            </svg>
        </div>
        <!-- Body -->
        <div class="house-body">
            <!-- Windows grid 2x2 -->
            <div class="house-windows">
                <div class="house-window"></div>
                <div class="house-window"></div>
                <div class="house-window"></div>
                <div class="house-window"></div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
interface Props {
    size?: 'sm' | 'md' | 'lg'
    rotation?: number
}

const props = withDefaults(defineProps<Props>(), {
    size: 'md',
    rotation: 0
})

const sizeMap = {
    sm: { width: '60px', bodyHeight: '70px', roofHeight: '40px' },
    md: { width: '100px', bodyHeight: '120px', roofHeight: '70px' },
    lg: { width: '140px', bodyHeight: '160px', roofHeight: '90px' }
}

const houseStyle = computed(() => ({
    '--house-width': sizeMap[props.size].width,
    '--body-height': sizeMap[props.size].bodyHeight,
    '--roof-height': sizeMap[props.size].roofHeight,
    transform: `rotate(${props.rotation}deg)`
}))
</script>

<style scoped>
.house {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: var(--house-width, 100px);
    transform-origin: center bottom;
}

.house-roof {
    width: 100%;
    height: var(--roof-height, 70px);
    margin-bottom: -2px;
    position: relative;
    z-index: 2;
}

.house-body {
    width: 80%;
    height: var(--body-height, 120px);
    background-color: #FFFF00;
    border: 4px solid #FF00CF;
    border-top: none;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10%;
}

.house-windows {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 8%;
    width: 80%;
    height: 60%;
}

.house-window {
    background-color: #00FFC4;
    border: 2px solid #150059;
}
</style>
