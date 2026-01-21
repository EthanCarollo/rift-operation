/**
 * useBattleAnimation - Manages animation states for battle UI
 * 
 * Handles:
 * - Narrative text display with auto-hide
 * - Drawing validation feedback
 * - Flying image animation
 * - Victory message typewriter effect
 */

import { ref } from 'vue';
import type { Ref } from 'vue';
import { BATTLE_NARRATIVE, ATTACK_NARRATIVE } from '~/utils/battleConstants';

export function useBattleAnimation() {
    // --- NARRATIVE TEXT ---
    const showNarrativeText = ref(false);
    const narrativeText = ref('');
    const narrativeTimeout: Ref<NodeJS.Timeout | null> = ref(null);

    function showNarrative(text: string, duration: number = 4000) {
        if (narrativeTimeout.value) {
            clearTimeout(narrativeTimeout.value);
        }
        narrativeText.value = text;
        showNarrativeText.value = true;
        narrativeTimeout.value = setTimeout(() => {
            showNarrativeText.value = false;
        }, duration);
    }

    function showIntroNarrative() {
        showNarrative(BATTLE_NARRATIVE.intro, 6000);
    }

    function showAttackNarrative(attack: string) {
        if (attack && ATTACK_NARRATIVE[attack]) {
            showNarrative(ATTACK_NARRATIVE[attack], 4000);
        }
    }

    // --- DRAWING FEEDBACK ---
    const showDrawingFeedback = ref(false);
    const isDrawingValid = ref(false);
    const isGenerating = ref(false);
    let feedbackTimeout: NodeJS.Timeout | null = null;

    function showFeedback(valid: boolean, duration: number = 2000) {
        if (feedbackTimeout) clearTimeout(feedbackTimeout);
        isDrawingValid.value = valid;
        showDrawingFeedback.value = true;
        feedbackTimeout = setTimeout(() => {
            showDrawingFeedback.value = false;
        }, duration);
    }

    function setGenerating(value: boolean) {
        isGenerating.value = value;
    }

    // --- FLYING IMAGE ---
    const flyingImage: Ref<string | null> = ref(null);
    const animationInProgress = ref(false);

    function triggerFlyingAnimation(
        imageSrc: string,
        onComplete?: () => void
    ) {
        if (animationInProgress.value) {
            console.log('[Animation] Already in progress, skipping');
            return;
        }

        animationInProgress.value = true;
        console.log('[Animation] Starting flying image');

        // Small delay before showing image
        setTimeout(() => {
            flyingImage.value = imageSrc;
        }, 50);

        // After animation completes
        setTimeout(() => {
            flyingImage.value = null;
            animationInProgress.value = false;
            console.log('[Animation] Complete');
            onComplete?.();
        }, 1400);
    }

    // --- VICTORY MESSAGE ---
    const showVictoryMessage = ref(false);
    const displayedVictoryText = ref('');
    const victoryFullText = BATTLE_NARRATIVE.victory;

    function startVictoryMessage() {
        showVictoryMessage.value = true;
        typewriterEffect(victoryFullText);
    }

    function typewriterEffect(text: string, charDelay: number = 50) {
        displayedVictoryText.value = '';
        let i = 0;
        const interval = setInterval(() => {
            if (i < text.length) {
                displayedVictoryText.value += text.charAt(i);
                i++;
            } else {
                clearInterval(interval);
            }
        }, charDelay);
    }

    // --- RESET ---
    function resetAll() {
        showNarrativeText.value = false;
        showDrawingFeedback.value = false;
        isGenerating.value = false;
        flyingImage.value = null;
        animationInProgress.value = false;
        showVictoryMessage.value = false;
        displayedVictoryText.value = '';
    }

    return {
        // Narrative
        showNarrativeText,
        narrativeText,
        showNarrative,
        showIntroNarrative,
        showAttackNarrative,
        
        // Drawing feedback
        showDrawingFeedback,
        isDrawingValid,
        isGenerating,
        showFeedback,
        setGenerating,
        
        // Flying image
        flyingImage,
        animationInProgress,
        triggerFlyingAnimation,
        
        // Victory
        showVictoryMessage,
        displayedVictoryText,
        startVictoryMessage,
        
        // Utils
        resetAll,
    };
}
