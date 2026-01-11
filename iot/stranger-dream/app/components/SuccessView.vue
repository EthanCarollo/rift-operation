<template>
    <div class="success-view">
        <h1 class="success-title">Félicitations !</h1>
        <p class="success-text">
            Vous avez trouvé le prénom de l'inconnu qui hantait le cauchemar !
        </p>
        <p class="success-cta">
            Récupérez vite vos morceaux de faille !
        </p>
    </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.success-view {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    gap: 0.75rem;
    text-align: center;
}

.success-title {
    font-family: 'Lineal', sans-serif;
    font-weight: bold;
    font-size: 2.5rem;
    color: #FF00CF;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    margin: 0;
}

.success-text {
    font-family: 'Lineal', sans-serif;
    font-size: 2rem;
    color: #150059;
    line-height: 1.2;
    margin: 0;
    max-width: 580px;
}

.success-cta {
    font-family: 'Lineal', sans-serif;
    font-weight: bold;
    font-size: 2rem;
    color: #150059;
    line-height: 1.2;
    margin: 0;
    max-width: 560px;
}

@media (max-width: 768px) {
    .success-title {
        font-size: 2rem;
    }

    .success-text,
    .success-cta {
        font-size: 1.5rem;
    }
}

@media (max-width: 480px) {
    .success-title {
        font-size: 1.5rem;
    }

    .success-text,
    .success-cta {
        font-size: 1.125rem;
    }
}
</style>
