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
    title: "Question 1:",
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
    text: "Pour trouver la deuxième lettre, demande directemment à Cosmo le pinguin quelle est la lettre."
  },
  step_3: {
    type: 'puzzle',
    step: 3,
    title: "Question 3:",
    subtitle: "Pour trouver la troisième lettre, trouve le tour de cou de l'étranger qui hante le cauchemar.", 
    puzzleItems: [
      { image: '/images/stranger/shape-tie.png', symbol: '➤', letter: 'T' }, 
      { image: '/images/stranger/shape-bowtie.png', symbol: '➤', letter: 'U' }, // Correct for U
      { image: '/images/stranger/shape-monocle.png', symbol: '➤', letter: 'O' },
    ]
  },
  step_4: {
    type: 'text',
    step: 4,
    text: "La quatrième lettre se trouve derrière le moniteur de l'opérateur."
  },
}
