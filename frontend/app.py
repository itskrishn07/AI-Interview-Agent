import os
import json
import uuid
import requests
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="AI Technical Interview Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = os.getenv("API_URL", "http://localhost:8000/api/interview")
CANDIDATES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "candidates.json")

# Custom CSS for rich Aesthetics & Dark Mode polish
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #9CA3AF;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .badge-primary { background-color: #3B82F6; color: white; }
    .badge-success { background-color: #10B981; color: white; }
    .badge-warning { background-color: #F59E0B; color: white; }
    .badge-purple { background-color: #8B5CF6; color: white; }
    
    .feedback-section {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
    }
    .feedback-summary {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #E2E8F0;
        margin-bottom: 16px;
    }
    .strength-item {
        background-color: #064E3B;
        border-left: 4px solid #10B981;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        color: #D1FAE5;
    }
    .gap-item {
        background-color: #78350F;
        border-left: 4px solid #F59E0B;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        color: #FEF3C7;
    }
    .next-item {
        background-color: #1E3A8A;
        border-left: 4px solid #3B82F6;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        color: #DBEAFE;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load candidate dataset
@st.cache_data
def load_candidates():
    if os.path.exists(CANDIDATES_PATH):
        with open(CANDIDATES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("candidates", [])
    return []

candidates_list = load_candidates()

# Initialize Session State Variables
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "interview_done" not in st.session_state:
    st.session_state.interview_done = False
if "final_feedback" not in st.session_state:
    st.session_state.final_feedback = None
if "selected_candidate" not in st.session_state:
    st.session_state.selected_candidate = None
if "question_count" not in st.session_state:
    st.session_state.question_count = 0

# Header
st.markdown('<div class="main-header">AI Technical Interview Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Adaptive, multi-turn technical interviews grounded in the AI Cohort learning journey</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Candidate Setup")
    
    if candidates_list:
        candidate_options = {
            f"{c['member']['name']} ({c['member']['jobRole']}, {c['member']['yearsExperience']} yrs)": c
            for c in candidates_list
        }
        selected_key = st.selectbox("Select Candidate Profile:", list(candidate_options.keys()))
        current_cand_data = candidate_options[selected_key]
    else:
        st.error("candidates.json file not found.")
        current_cand_data = None

    if st.button("🚀 Start New Interview", type="primary", use_container_width=True):
        if current_cand_data:
            st.session_state.session_id = f"session-{uuid.uuid4().hex[:8]}"
            st.session_state.selected_candidate = current_cand_data
            st.session_state.messages = []
            st.session_state.interview_done = False
            st.session_state.final_feedback = None
            st.session_state.question_count = 1

            # Call Backend API to initialize interview
            try:
                payload = {
                    "sessionId": st.session_state.session_id,
                    "candidate": current_cand_data
                }
                res = requests.post(API_URL, json=payload, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.messages.append({"role": "assistant", "content": data["reply"]})
                    st.session_state.interview_done = data.get("done", False)
                else:
                    st.error(f"Backend API error: {res.status_code} - {res.text}")
            except Exception as e:
                st.error(f"Could not connect to backend API at {API_URL}: {e}")

    st.divider()

    # Candidate Profile Display
    if st.session_state.selected_candidate:
        cand = st.session_state.selected_candidate["member"]
        signals = st.session_state.selected_candidate.get("signals", {})
        missions = st.session_state.selected_candidate.get("missions", [])

        st.markdown(f"### 👤 {cand['name']}")
        st.markdown(f"**Role**: {cand['jobRole']}")
        st.markdown(f"**Experience**: {cand['yearsExperience']} years")
        st.markdown(f"**Education**: {cand['education']}")
        st.markdown(f"**Missions First-Try**: {signals.get('missionsFirstTry', 0)} / {signals.get('missionsCompleted', 0)}")

        first_try_days = [m["day"] for m in missions if m.get("passed") and m.get("attempts") == 1]
        skipped_days = [m["day"] for m in missions if m.get("skipped")]

        st.markdown("**Completed First-Try:**")
        st.markdown(" ".join([f'<span class="badge badge-success">Day {d}</span>' for d in first_try_days[:6]]), unsafe_allow_html=True)

        if skipped_days:
            st.markdown("**Skipped Topics:**")
            st.markdown(" ".join([f'<span class="badge badge-warning">Day {d}</span>' for d in skipped_days]), unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📊 Interview Progress")
        progress_val = min(st.session_state.question_count / 8.0, 1.0)
        st.progress(progress_val)
        st.caption(f"Questions: {st.session_state.question_count} / 8+ (Min 4 Curriculum Days Required)")

# Main Chat Interface
if not st.session_state.session_id:
    st.info("👈 Select a candidate profile from the sidebar and click **Start New Interview** to begin.")
else:
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Final Feedback Display Card
    if st.session_state.interview_done and st.session_state.final_feedback:
        st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
        st.markdown("## 🎯 Final Interview Assessment & Feedback")
        
        fb = st.session_state.final_feedback
        st.markdown(f'<div class="feedback-summary">{fb.get("summary", "")}</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💪 Strengths Demonstrated")
            for s in fb.get("strengths", []):
                st.markdown(f'<div class="strength-item">✓ {s}</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("### 🔍 Technical Gaps Identified")
            for g in fb.get("gaps", []):
                st.markdown(f'<div class="gap-item">⚠ {g}</div>', unsafe_allow_html=True)

        st.markdown("### 📚 Actionable Next Steps")
        for n in fb.get("next", []):
            st.markdown(f'<div class="next-item">➔ {n}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Chat Input
    elif not st.session_state.interview_done:
        if user_input := st.chat_input("Type your technical response..."):
            # Append candidate response to chat view
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            # Call Backend API
            try:
                payload = {
                    "sessionId": st.session_state.session_id,
                    "message": user_input
                }
                res = requests.post(API_URL, json=payload, timeout=20)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.question_count += 1
                    st.session_state.interview_done = data.get("done", False)
                    reply_text = data.get("reply", "")
                    
                    st.session_state.messages.append({"role": "assistant", "content": reply_text})
                    with st.chat_message("assistant"):
                        st.write(reply_text)

                    if data.get("done") and data.get("feedback"):
                        st.session_state.final_feedback = data.get("feedback")
                        st.rerun()
                else:
                    st.error(f"Error from API: {res.status_code} - {res.text}")
            except Exception as e:
                st.error(f"Failed to communicate with backend API: {e}")
