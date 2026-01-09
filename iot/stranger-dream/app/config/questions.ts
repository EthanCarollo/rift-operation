export type PuzzleItem = {
  image: string;
  symbol: string; // The arrow or indicator
  letter: string;
}

export type Question = {
  type: 'text' | 'puzzle'; // Renamed 'hat-puzzle' to generic 'puzzle'
  title?: string;
  subtitle?: string;
  step: number;
  text?: string;
  puzzleItems?: PuzzleItem[];
}

export const questions: Record<string, Question> = {
  active: {
    type: 'puzzle',
    step: 1,
    title: "Étape 1:",
    subtitle: "Pour trouver la première lettre, trouve le chapeau de l'étranger qui hante le cauchemar.",
    puzzleItems: [
      { image: '/images/stranger/hat-star.png', symbol: '➤', letter: 'B' },
      { image: '/images/stranger/hat-stripe.png', symbol: '➤', letter: 'i' },
      { image: '/images/stranger/hat-stripes.png', symbol: '➤', letter: 'P' },
    ]
  },
  step_2: {
    type: 'text',
    step: 2,
    text: "Trouvez le point faible de Dark Cosmo et dites-le lui."
  },
  step_3: {
    type: 'text',
    step: 3,
    text: "Demandez gentiment la lettre à Cosmo le pingouin."
  },
  step_4: {
    type: 'text',
    step: 4,
    text: "Ramenez Dark Cosmo à la lumière dans son foyer."
  },
}
