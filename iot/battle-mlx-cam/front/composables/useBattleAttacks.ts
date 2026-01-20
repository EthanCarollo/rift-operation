import { ref, computed } from 'vue';

export function useBattleAttacks() {
    const ATTACKS = ['BOUCLIER', 'PLUIE', 'LUNE'];

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
        // Deterministic mode (Sync) - 3 HP phases
        if (hp !== undefined && hp > 0 && hp <= 3) {
            // Map HP 3->1 to Indices 0->2
            // HP 3 -> Index 0 (BOUCLIER)
            // HP 2 -> Index 1 (PLUIE)
            // HP 1 -> Index 2 (LUNE)
            const index = 3 - hp;
            const nextAttack = ATTACKS[index % ATTACKS.length]!;

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
