import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import candidateData from '../../../candidates.json';
import Navbar from '../components/Navbar';
import CandidateCard from '../components/CandidateCard';
import Button from '../components/Button';

const candidates = candidateData.candidates.map((apiCandidate) => {
  const { member, missions = [], signals = {} } = apiCandidate;
  const completed = missions.filter((mission) => mission.passed).length;
  const attempts = missions.reduce((total, mission) => total + (mission.attempts || 0), 0);
  const skippedTopics = missions.filter((mission) => mission.skipped).map((mission) => mission.title);

  return {
    id: member.id,
    name: member.name,
    role: member.jobRole,
    experience: member.yearsExperience,
    education: member.education,
    completedMissions: signals.missionsCompleted ?? completed,
    attempts,
    skippedTopics,
    learningSignals: {
      commitDays: signals.commitDays || 0,
      firstTry: signals.missionsFirstTry || 0,
      status: signals.commitDays >= 28 ? 'High momentum' : 'Consistent learner'
    },
    apiCandidate
  };
});

export default function Candidates() {
  const [selected, setSelected] = useState(null);
  const navigate = useNavigate();

  const continueToInterview = () => {
    if (!selected) return;
    sessionStorage.setItem('intervista-candidate', JSON.stringify(selected));
    sessionStorage.removeItem('intervista-results');
    navigate('/interview');
  };

  return <div className="app-shell"><Navbar /><main className="candidates-page"><section className="page-intro"><div><div className="eyebrow"><i /> Step 01 / Candidate context</div><h1>Who are we<br /><em>meeting?</em></h1><p>Select one candidate. Their learning journey gives InterVista the context to make every question count.</p></div><div className="selection-count"><b>{selected ? '01' : '00'}</b><span>candidate selected</span></div></section><section className="candidate-grid">{candidates.map((candidate) => <CandidateCard key={candidate.id} candidate={candidate} selected={selected?.id === candidate.id} onSelect={setSelected} />)}</section><div className="selection-bar"><div>{selected ? <><span className="active-choice">✓</span> <b>{selected.name}</b> selected for interview</> : 'Select a candidate to begin'}</div><Button disabled={!selected} onClick={continueToInterview}>Continue to interview</Button></div></main></div>;
}
