export type PuzzleItem = {
  image: string;
  symbol: string; // The arrow or indicator
  letter: string;
}

export type Question = {
  type: 'text' | 'puzzle';
  title?: string;
  subtitle?: string;
  step: number;
  text?: string;
  image?: string;
  images?: string[];
  imagePosition?: 'top' | 'bottom';
  puzzleItems?: PuzzleItem[];
}

export const questions: Record<string, Question> = {
  active: {
    type: 'puzzle',
    step: 1,
    title: "QUESTION 1 :",
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
    title: "QUESTION 2 :",
    text: "Pour trouver la 2ème lettre, trouve le point faible du pingouin Dark Cosmo et dis-le lui.",
    image: '/images/stranger/dark-cosmo.png',
    imagePosition: 'bottom'
  },
  step_3: {
    type: 'text',
    step: 3,
    text: "Demandez gentiment la lettre à Cosmo le pingouin.",
    image: '/images/stranger/cosmo.png',
    imagePosition: 'bottom'
  },
  step_4: {
    type: 'text',
    step: 4,
    text: "Ramenez Dark Cosmo à la lumière dans son foyer.",
    images: ['/images/stranger/dark-cosmo.png', '/images/stranger/cosmo.png']
  },
}
