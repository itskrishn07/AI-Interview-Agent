import { Link, Navigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Button from '../components/Button';

export default function Results() {
  let feedback;
  let candidate;
  try {
    feedback = JSON.parse(sessionStorage.getItem('intervista-results'));
    candidate = JSON.parse(sessionStorage.getItem('intervista-candidate'));
  } catch { /* session data is unavailable */ }

  if (!feedback || !candidate) return <Navigate to="/candidates" replace />;
  const hasScore = typeof feedback.score === 'number';

  return <div className="app-shell results-page"><Navbar /><main><section className="results-hero"><div className="completion-mark">✓</div><div className="eyebrow"><i /> Interview complete</div><h1>A clearer view of<br /><em>{candidate.name.split(' ')[0]}'s potential.</em></h1><p>{feedback.summary}</p></section><section className="score-row"><article className="score-card"><span>{hasScore ? 'Overall score' : 'Interview status'}</span><div><b>{hasScore ? feedback.score : '✓'}</b>{hasScore && <small>/100</small>}</div><p>{hasScore ? 'Strong technical judgment' : 'Personalized feedback is ready.'}</p></article><article className="summary-card"><span>Interview lens</span><h3>{candidate.role}</h3><p>Adaptive technical questions shaped by the candidate's actual learning journey.</p>{hasScore && <div className="score-bar"><i style={{ width: `${feedback.score}%` }} /></div>}</article></section><section className="feedback-grid"><FeedbackCard number="01" title="Strengths" items={feedback.strengths} tone="positive" /><FeedbackCard number="02" title="Areas to improve" items={feedback.gaps} tone="neutral" /><FeedbackCard number="03" title="Recommended next steps" items={feedback.next} tone="next" /></section><div className="new-interview"><div><div className="eyebrow"><i /> Keep exploring</div><h2>Ready for another<br />perspective?</h2></div><Link to="/candidates"><Button>Start new interview</Button></Link></div></main></div>;
}

function FeedbackCard({ number, title, items, tone }) {
  return <article className={`feedback-card ${tone}`}><span>{number}</span><h3>{title}</h3><ul>{items.map((item) => <li key={item}><b>{tone === 'positive' ? '✓' : '→'}</b>{item}</li>)}</ul></article>;
}
