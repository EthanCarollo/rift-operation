export const DEVICE_ID = 'boss-workshop-website';
export const APPEARING_DURATION = 10000; // 10 seconds
export const HIT_DURATION = 1000; // 1 second before next state
export const VOLUME_RESTORE_DELAY = 1000; // 1 second after hit

// Video assets by state
export const BATTLE_VIDEOS: Record<string, string | null> = {
    idle: null,
    APPEARING: '/battle-workshop/video-battle-appearing.mp4',
    FIGHTING: '/battle-workshop/video-battle-fighting.mp4',
    HIT: '/battle-workshop/video-battle-hit.mp4',
    WEAKENED: '/battle-workshop/video-battle-weakened.mp4',
    CAPTURED: '/battle-workshop/video-battle-captured.mp4'
};
// Music assets by state
export const BATTLE_MUSIC: Record<string, string | null> = {
    idle: null,
    APPEARING: '/battle-workshop/music-battle-intro.mp3',
    FIGHTING: '/battle-workshop/music-battle-combat.mp3',
    HIT: null, // No music change, use SFX
    WEAKENED: null, // No music - just silence for dramatic effect
    CAPTURED: null  // No victory music
};
// Sound effects
export const BATTLE_SFX = {
    hit: '/battle-workshop/sfx-battle-hit.mp3'
};

// State configuration for transitions
export interface StateConfig {
    video: string | null;
    music: string | null;
    loop: boolean;
    message?: string;
    subMessage?: string;
    messageClass?: string;
    clearAttack?: boolean;
}

export const BATTLE_STATE_CONFIG: Record<string, StateConfig> = {
    IDLE: {
        video: null,
        music: null,
        loop: false
    },
    APPEARING: {
        video: BATTLE_VIDEOS.APPEARING ?? null,
        music: BATTLE_MUSIC.APPEARING ?? null,
        loop: true
    },
    FIGHTING: {
        video: BATTLE_VIDEOS.FIGHTING ?? null,
        music: BATTLE_MUSIC.FIGHTING ?? null,
        loop: true
    },
    HIT: {
        video: BATTLE_VIDEOS.HIT ?? null,
        music: null,
        loop: true,
        message: 'HIT',
        messageClass: 'text-red-500 animate-pulse'
    },
    WEAKENED: {
        video: BATTLE_VIDEOS.WEAKENED ?? null,
        music: BATTLE_MUSIC.WEAKENED ?? null,
        loop: true,
        message: "L'INCONNU EST AFFAIBLI",
        subMessage: "Utilisez les sceaux de confinement de la BRC pour le mettre hors d'état de nuire !",
        messageClass: 'text-purple-400',
        clearAttack: true
    },
    CAPTURED: {
        video: BATTLE_VIDEOS.CAPTURED ?? null,
        music: BATTLE_MUSIC.CAPTURED ?? null,
        loop: false,
        message: 'MENACE NEUTRALISÉE',
        messageClass: 'text-green-400',
        clearAttack: true
    }
};

// Battle states enum for type safety
export type BattleState = 'IDLE' | 'ACTIVE' | 'APPEARING' | 'FIGHTING' | 'HIT' | 'WEAKENED' | 'CAPTURED' | 'DONE';

// Initial values
export const INITIAL_HP = 3;
export const START_CONDITION_PARTS = 4;

// Narrative text for immersive battle experience
export const BATTLE_NARRATIVE = {
    intro: "Vous avez retrouvé l'inconnu dans la forêt...",
    phase1: "Il se munit d'un bouclier, vous devez dessiner quelque chose pour l'enlever",
    phase2: "Il appelle ensuite la pluie pour vous ralentir, essayez de vous en protéger",
    phase3: "Il plonge ensuite le monde dans le noir complet, comment rétablir le soleil",
    victory: "Vous avez réussi à vous débarrasser de l'inconnu, il quitte le sommeil de la petite fille..."
};

// Attack name to narrative text mapping
export const ATTACK_NARRATIVE: Record<string, string> = {
    'BOUCLIER': BATTLE_NARRATIVE.phase1,
    'PLUIE': BATTLE_NARRATIVE.phase2,
    'LUNE': BATTLE_NARRATIVE.phase3,
};

