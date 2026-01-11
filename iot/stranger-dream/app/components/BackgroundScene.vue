<template>
    <div class="background-scene">
        <!-- Sky (green background) -->
        <div class="sky"></div>

        <!-- Hills (ellipses) - layered for depth -->
        <div class="hills">
            <!-- Back hill (largest, darkest) -->
            <div class="hill hill-back"></div>
            <!-- Middle hill right -->
            <div class="hill hill-middle-right"></div>
            <!-- Middle hill left -->
            <div class="hill hill-middle-left"></div>
            <!-- Front hill -->
            <div class="hill hill-front"></div>
            <!-- Bottom fill -->
            <div class="hill hill-bottom"></div>
        </div>

        <!-- Decorative elements -->
        <div class="decorations">
            <!-- Houses -->
            <House class="decoration house-top-left" size="md" :rotation="-5" />
            <House class="decoration house-top-right" size="lg" :rotation="0" />

            <!-- Lollipops -->
            <Lollipop class="decoration lollipop-left-1" color="rose" size="sm" :rotation="-15" />
            <Lollipop class="decoration lollipop-left-2" color="green" size="md" :rotation="5" />
            <Lollipop class="decoration lollipop-center" color="yellow" size="sm" :rotation="-5" />
            <Lollipop class="decoration lollipop-right-1" color="green" size="md" :rotation="10" />
            <Lollipop class="decoration lollipop-right-2" color="yellow" size="lg" :rotation="-8" />
        </div>
    </div>
</template>

<script setup lang="ts">
import House from './House.vue'
import Lollipop from './Lollipop.vue'
</script>

<style scoped>
.background-scene {
    position: fixed;
    inset: 0;
    overflow: hidden;
    z-index: 0;
}

.sky {
    position: absolute;
    inset: 0;
    background-color: #00FFC4;
}

.hills {
    position: absolute;
    inset: 0;
    pointer-events: none;
}

.hill {
    position: absolute;
    border-radius: 50%;
}

/* Back hill - darkest purple */
.hill-back {
    width: 120%;
    height: 60%;
    bottom: -10%;
    left: -10%;
    background-color: #8B008B;
}

/* Middle right hill */
.hill-middle-right {
    width: 80%;
    height: 50%;
    bottom: 0;
    right: -20%;
    background-color: #9B1B9B;
}

/* Middle left hill */
.hill-middle-left {
    width: 70%;
    height: 50%;
    bottom: -5%;
    left: -10%;
    background-color: #AB2BAB;
}

/* Front hill - brightest magenta */
.hill-front {
    width: 90%;
    height: 45%;
    bottom: -20%;
    left: 20%;
    background-color: #FF00CF;
}

/* Bottom solid fill */
.hill-bottom {
    width: 120%;
    height: 25%;
    bottom: -5%;
    left: -10%;
    background-color: #FF00CF;
    border-radius: 0;
}

.decorations {
    position: absolute;
    inset: 0;
    pointer-events: none;
}

.decoration {
    position: absolute;
}

/* House positions */
.house-top-left {
    top: 8%;
    left: 15%;
}

.house-top-right {
    top: 5%;
    right: 5%;
}

/* Lollipop positions */
.lollipop-left-1 {
    top: 10%;
    left: 3%;
}

.lollipop-left-2 {
    bottom: 25%;
    left: 15%;
}

.lollipop-center {
    bottom: 30%;
    left: 35%;
}

.lollipop-right-1 {
    bottom: 20%;
    right: 25%;
}

.lollipop-right-2 {
    bottom: 15%;
    right: 8%;
}
</style>
