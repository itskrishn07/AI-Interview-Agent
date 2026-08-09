const delay = (ms = 650) => new Promise((resolve) => setTimeout(resolve, ms));

const interview = [
  { topic: 'System design', question: 'You are designing a service that ingests millions of events per day. How would you make the ingestion pipeline reliable and scalable?' },
  { topic: 'Data modeling', question: 'What trade-offs would you weigh when choosing between a normalized relational model and a document model for this system?' },
  { topic: 'APIs & contracts', question: 'How would you design an API contract that lets downstream teams evolve independently?' },
  { topic: 'Performance', question: 'A critical endpoint is slow at peak traffic. Walk me through how you would investigate and improve it.' },
  { topic: 'Distributed systems', question: 'How would you approach idempotency when a background job can be retried multiple times?' },
  { topic: 'Security', question: 'What practical steps would you take to protect sensitive customer data in transit and at rest?' },
  { topic: 'Observability', question: 'Which signals would you instrument first so an on-call engineer can diagnose a production incident quickly?' },
  { topic: 'Leadership', question: 'Tell me how you would communicate a high-risk technical trade-off to both engineers and non-technical stakeholders.' }
];

const feedback = (candidate) => ({
  summary: `${candidate.name} demonstrated a thoughtful, structured approach to technical decision-making. Their responses connected implementation choices to reliability, team impact, and user outcomes.`,
  strengths: ['Frames ambiguous problems before proposing solutions', 'Balances scale, reliability, and delivery trade-offs', 'Communicates technical choices with clarity'],
  gaps: ['Add more concrete metrics when describing impact', 'Call out failure modes earlier in the design process'],
  next: ['Practice concise architecture walkthroughs with measurable outcomes', 'Deepen examples around incident response and observability', 'Prepare one leadership story that illustrates technical influence'],
  score: 86
});

export async function startMockInterview({ candidate }) {
  await delay(850);
  return { reply: `Welcome, ${candidate.name.split(' ')[0]}. I’ve reviewed your learning journey and will tailor this conversation to your experience. Let’s begin.\n\n${interview[0].question}`, done: false, questionNumber: 1, topic: interview[0].topic };
}

export async function sendMockMessage({ candidate, questionNumber }) {
  await delay(850);
  if (questionNumber >= interview.length) return { reply: 'Thank you — that completes the interview. I’m preparing your personalized feedback now.', done: true, feedback: feedback(candidate), questionNumber: interview.length, topic: interview.at(-1).topic };
  const next = interview[questionNumber];
  return { reply: `Thank you. I’d like to build on that.\n\n${next.question}`, done: false, questionNumber: questionNumber + 1, topic: next.topic };
}
