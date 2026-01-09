import { ref, computed } from 'vue';

export function useBattleAttacks() {
    const ATTACKS = ['PORTE', 'ÉTOILE', 'OEIL', 'NUAGE', 'CLÉ'];

    const attackHistory = ref<string[]>([]);
    const currentAttack = ref<string | null>(null);

    // Count occurrences of each attack
    const attackCounts = computed(() => {
        const counts: Record<string, number> = {};
        ATTACKS.forEach(attack => counts[attack] = 0);
        attackHistory.value.forEach(attack => {
            if (counts[attack] !== undefined) counts[attack]++;
        });
        return counts;
    });

    function getNextAttack(hp?: number) {
        // Deterministic mode (Sync)
        if (hp !== undefined && hp > 0 && hp <= 5) {
            // Map HP 5->1 to Indices 0->4
            // HP 5 -> Index 0
            // HP 4 -> Index 1
            const index = 5 - hp;
            const nextAttack = ATTACKS[index % ATTACKS.length];

            // Update state
            attackHistory.value.push(nextAttack);
            currentAttack.value = nextAttack;
            return nextAttack;
        }

        // Fallback Random Logic (Legacy/Dev)
        const availableAttacks = ATTACKS.filter(attack => {
            if ((attackCounts.value[attack] ?? 0) >= 3) return false;
            const lastAttack = attackHistory.value[attackHistory.value.length - 1];
            if (lastAttack === attack) return false;
            return true;
        });

        if (availableAttacks.length === 0) {
            console.warn('[Battle] No available attacks, resetting history');
            attackHistory.value = [];
            return ATTACKS[Math.floor(Math.random() * ATTACKS.length)];
        }

        const nextAttack = availableAttacks[Math.floor(Math.random() * availableAttacks.length)];
        if (nextAttack) {
            attackHistory.value.push(nextAttack);
            currentAttack.value = nextAttack;
        }

        return nextAttack ?? '';
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
