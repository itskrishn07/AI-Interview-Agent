export default function CandidateCard({ candidate, selected, onSelect }) {
  const initials = candidate.name.split(' ').map((part) => part[0]).join('');
  return <button className={`candidate-card ${selected ? 'selected' : ''}`} onClick={() => onSelect(candidate)} aria-pressed={selected}>
    <div className="card-top"><div className="avatar">{initials}</div><div><h3>{candidate.name}</h3><p>{candidate.role}</p></div><span className="select-ring">{selected && '✓'}</span></div>
    <div className="candidate-details"><span>{candidate.experience} {candidate.experience === 1 ? 'year' : 'years'} exp.</span><span>{candidate.education}</span></div>
    <div className="mission-row"><span>Learning journey</span><b>{candidate.completedMissions}/31 missions</b></div><div className="progress-track"><i style={{ width: `${(candidate.completedMissions / 31) * 100}%` }} /></div>
    <div className="signal"><span className="signal-dot" />{candidate.learningSignals.status}<small>{candidate.learningSignals.commitDays} active days</small></div>
  </button>;
}
