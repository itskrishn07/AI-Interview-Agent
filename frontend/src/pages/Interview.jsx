import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ChatMessage from '../components/ChatMessage';
import CandidatePanel from '../components/CandidatePanel';
import InterviewProgress from '../components/InterviewProgress';
import LoadingIndicator from '../components/LoadingIndicator';
import { startInterview, sendInterviewMessage } from '../services/api';

const topics = [
  'System design',
  'Data modeling',
  'APIs & contracts',
  'Performance',
  'Distributed systems',
  'Security',
  'Observability',
  'Leadership'
];

export default function Interview() {
  const navigate = useNavigate();
  const conversationRef = useRef(null);
  const endRef = useRef(null);
  const startRequested = useRef(false);

  const [candidate] = useState(() => {
    try {
      return JSON.parse(sessionStorage.getItem('intervista-candidate'));
    } catch {
      return null;
    }
  });

  const [messages, setMessages] = useState([]);
  const [questionNumber, setQuestionNumber] = useState(0);
  const [input, setInput] = useState('');
  const [thinking, setThinking] = useState(false);
  const [error, setError] = useState('');
  const [started, setStarted] = useState(false);

  useEffect(() => {
    if (!candidate) {
      navigate('/candidates', { replace: true });
      return;
    }
    if (startRequested.current) return;
    startRequested.current = true;

    const sessionId = crypto.randomUUID();
    sessionStorage.setItem('intervista-session-id', sessionId);
    setThinking(true);

    startInterview({ sessionId, candidate })
      .then((result) => {
        setMessages([{ role: 'ai', text: result.reply }]);
        setQuestionNumber(1);
        setStarted(true);
      })
      .catch((requestError) => setError(requestError.message || 'Unable to connect to InterVista. Please try again.'))
      .finally(() => setThinking(false));
  }, [candidate, navigate]);

  useEffect(() => {
    if (conversationRef.current) {
      conversationRef.current.scrollTop = conversationRef.current.scrollHeight;
    }
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, thinking]);

  const submit = async (event) => {
    if (event) event.preventDefault();
    const message = input.trim();
    if (!message || thinking || !started) return;

    setMessages((current) => [...current, { role: 'candidate', text: message }]);
    setInput('');
    setThinking(true);
    setError('');

    try {
      const result = await sendInterviewMessage({
        sessionId: sessionStorage.getItem('intervista-session-id'),
        message,
        candidate,
        questionNumber
      });
      setMessages((current) => [...current, { role: 'ai', text: result.reply }]);

      if (result.done) {
        sessionStorage.setItem('intervista-results', JSON.stringify(result.feedback));
        window.setTimeout(() => navigate('/results'), 850);
      } else {
        setQuestionNumber((current) => current + 1);
      }
    } catch (requestError) {
      setError(requestError.message || 'Unable to connect to InterVista. Please try again.');
    } finally {
      setThinking(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="app-shell interview-page">
      <Navbar />
      <main className="interview-layout">
        <section className="interview-main">
          <div className="interview-header">
            <div>
              <div className="eyebrow"><i /> Live interview</div>
              <h1>{started ? `Question ${questionNumber} of 8` : 'Preparing interview'}</h1>
            </div>
            <div className="question-pill">{questionNumber || '—'} <span>/ 8+</span></div>
          </div>

          <div className="conversation" ref={conversationRef}>
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {thinking && <LoadingIndicator />}
            {error && <p className="form-error">{error}</p>}
            <div ref={endRef} />
          </div>

          <form className="answer-form" onSubmit={submit}>
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={thinking ? 'InterVista is preparing the next prompt…' : 'Share your response. Be specific about your approach and trade-offs.'}
              disabled={thinking || !started}
              rows="3"
            />
            <div>
              <span>↵ Enter to submit (Shift+Enter for new line)</span>
              <button disabled={!input.trim() || thinking || !started} type="submit">
                Submit answer <b>↑</b>
              </button>
            </div>
          </form>
        </section>

        <aside>
          <CandidatePanel candidate={candidate} questionNumber={questionNumber} />
          <InterviewProgress questionNumber={questionNumber} topics={topics} />
        </aside>
      </main>
    </div>
  );
}
