<template>
    <div class="candy-container">
        <!-- Left star spikes (2 triangles) -->
        <svg class="star-spike star-left" viewBox="0 0 120 200" preserveAspectRatio="none">
            <!-- Upper triangle -->
            <polygon points="120,60 0,0 60,60" fill="#FFFF00" />
            <!-- Lower triangle -->
            <polygon points="120,140 0,200 60,140" fill="#FFFF00" />
            <!-- Connector -->
            <polygon points="120,60 60,60 60,140 120,140" fill="#FFFF00" />
        </svg>

        <!-- Main oval body -->
        <div class="candy-body">
            <!-- Main content slot -->
            <div class="candy-content">
                <slot></slot>
            </div>

            <!-- Pagination slot (inside at bottom) -->
            <div class="candy-pagination">
                <slot name="pagination"></slot>
            </div>
        </div>

        <!-- Right star spikes (2 triangles) -->
        <svg class="star-spike star-right" viewBox="0 0 120 200" preserveAspectRatio="none">
            <!-- Upper triangle -->
            <polygon points="0,60 120,0 60,60" fill="#FFFF00" />
            <!-- Lower triangle -->
            <polygon points="0,140 120,200 60,140" fill="#FFFF00" />
            <!-- Connector -->
            <polygon points="0,60 60,60 60,140 0,140" fill="#FFFF00" />
        </svg>
    </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.candy-container {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    max-width: 1000px;
    margin: 0 auto;
}

.candy-body {
    background-color: #FFFF00;
    border-radius: 50%;
    aspect-ratio: 1.2 / 1;
    width: 100%;
    max-width: 680px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    padding: 50px 70px 30px;
    position: relative;
    z-index: 2;
    text-align: center;
}

.candy-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
}

.candy-pagination {
    padding-top: 0.5rem;
    width: 100%;
}

.star-spike {
    position: absolute;
    height: 60%;
    width: auto;
    z-index: 1;
}

.star-left {
    left: 0;
    transform: translateX(-65%);
}

.star-right {
    right: 0;
    transform: translateX(65%);
}

@media (max-width: 768px) {
    .candy-body {
        padding: 35px 45px 20px;
    }

    .star-spike {
        height: 45%;
    }
}
</style>
