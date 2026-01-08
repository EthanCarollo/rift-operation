// Composable for Battle Attack Logic
import { ref, computed } from 'vue';

export function useBattleAttacks() {
    const ATTACKS = ['PORTE', 'ÉTOILE', 'OEIL', 'NUAGE', 'CLÉ'];

    const attackHistory = ref([]);
    const currentAttack = ref(null);

    // Count occurrences of each attack
    const attackCounts = computed(() => {
        const counts = {};
        ATTACKS.forEach(attack => counts[attack] = 0);
        attackHistory.value.forEach(attack => {
            if (counts[attack] !== undefined) counts[attack]++;
        });
        return counts;
    });

    // Get next random attack with constraints
    function getNextAttack() {
        const availableAttacks = ATTACKS.filter(attack => {
            // Rule 1: Max 3 occurrences
            if (attackCounts.value[attack] >= 3) return false;

            // Rule 2: No consecutive duplicates
            const lastAttack = attackHistory.value[attackHistory.value.length - 1];
            if (lastAttack === attack) return false;

            return true;
        });

        // If no attacks available (shouldn't happen with 5 attacks), reset history
        if (availableAttacks.length === 0) {
            console.warn('[Battle] No available attacks, resetting history');
            attackHistory.value = [];
            return ATTACKS[Math.floor(Math.random() * ATTACKS.length)];
        }

        // Pick random from available
        const nextAttack = availableAttacks[Math.floor(Math.random() * availableAttacks.length)];
        attackHistory.value.push(nextAttack);
        currentAttack.value = nextAttack;

        return nextAttack;
    }

    function resetAttacks() {
        attackHistory.value = [];
        currentAttack.value = null;
    }

    return {
        currentAttack,
        attackHistory,
        attackCounts,
        getNextAttack,
        resetAttacks
    };
}
