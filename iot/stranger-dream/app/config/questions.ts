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
    subtitle: "<b>Pour trouver la première lettre</b>, trouve le chapeau de l'inconnu qui hante le cauchemar.",
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
    text: "<b>Pour trouver la 2ème lettre</b>, trouve le point faible du pingouin <b>Dark Cosmo</b> et dis-le lui.",
    image: '/images/stranger/dark-cosmo.png',
    imagePosition: 'bottom'
  },
  step_3: {
    type: 'text',
    step: 3,
    text: "<b>Pour trouver la 3ème lettre</b>, demande gentiment la lettre à <b>Cosmo</b> le pingouin en lui parlant.",
    image: '/images/stranger/cosmo.png',
    imagePosition: 'bottom'
  },
  step_4: {
    type: 'text',
    step: 4,
    text: "<b>Pour trouver la dernière lettre</b>, prenez <b>Dark Cosmo</b> et posez-le sur son socle à côté de <b>Cosmo</b>.",
    image: '/images/stranger/dark-cosmo+cosmo.png',
    imagePosition: 'bottom'
  },
  recognized: {
    type: 'text',
    step: 5,
    text: "Paul a été reconnu !",
    image: '/images/stranger/cosmo.png',
    imagePosition: 'bottom'
  }
}
