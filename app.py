import streamlit as st
import anthropic
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Election Commission Assistant",
    page_icon="🗳",
    layout="wide"
)

# ---------------- STYLES ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600&display=swap');

* { font-family: 'Sora', sans-serif; }

.stApp {
    background: #f8f9fc;
}

.header-box {
    display: flex;
    align-items: center;
    gap: 14px;
    background: white;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 16px;
    border: 1px solid #e8eaf0;
}

.header-icon {
    width: 48px; height: 48px;
    background: linear-gradient(135deg, #FF6B00, #FF9933);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
}

.header-title {
    font-size: 20px;
    font-weight: 600;
    color: #1a2340;
}

.header-sub {
    font-size: 13px;
    color: #888;
    margin-top: 2px;
}

.user-msg-wrap {
    display: flex;
    justify-content: flex-end;
    margin: 6px 0;
}

.user-msg {
    background: #FF6B00;
    color: white;
    padding: 10px 16px;
    border-radius: 16px 16px 4px 16px;
    max-width: 75%;
    font-size: 14px;
    line-height: 1.6;
}

.bot-msg-wrap {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 10px;
    margin: 6px 0;
}

.bot-avatar {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #FF6B00, #FF9933);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px;
    font-weight: 600;
    color: white;
    flex-shrink: 0;
    margin-top: 2px;
}

.bot-msg {
    background: white;
    color: #1a2340;
    padding: 10px 16px;
    border-radius: 4px 16px 16px 16px;
    max-width: 75%;
    font-size: 14px;
    line-height: 1.6;
    border: 1px solid #e8eaf0;
}

.status-bar {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #888;
    margin-top: 8px;
}

.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #138808;
    display: inline-block;
}

.chip-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 12px;
}

.chip {
    background: white;
    border: 1px solid #e8eaf0;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 12px;
    color: #555;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="header-box">
    <div class="header-icon">🗳</div>
    <div>
        <div class="header-title">Election Commission Assistant</div>
        <div class="header-sub">AI-powered guidance for Indian elections &amp; general queries</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")

    language = st.selectbox("🌐 Language", ["English", "Tamil (தமிழ்)"])

    st.markdown("---")
    st.markdown("### 💡 Quick Questions")
    quick_questions = [
        "How do I register to vote?",
        "What is EVM and is it safe?",
        "What is Model Code of Conduct?",
        "How are election winners decided?",
        "What is NOTA?",
        "How to apply for Voter ID card?",
        "What is VVPAT?",
        "Can NRIs vote in Indian elections?",
    ]

    for q in quick_questions:
        if st.button(q, use_container_width=True, key=f"chip_{q}"):
            st.session_state.pending_input = q

    st.markdown("---")
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.api_messages = []
        st.rerun()

    st.markdown("""
    <div class="status-bar">
        <span class="status-dot"></span>
        Claude AI · Powered by Anthropic
    </div>
    """, unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "api_messages" not in st.session_state:
    st.session_state.api_messages = []

if "pending_input" not in st.session_state:
    st.session_state.pending_input = ""

# ---------------- SYSTEM PROMPT ----------------
def get_system_prompt(language):
    lang_instruction = (
        "IMPORTANT: You MUST respond entirely in Tamil (தமிழ்). Use clear, simple Tamil language throughout."
        if "Tamil" in language
        else "Respond in clear, well-structured English."
    )

    return f"""You are a knowledgeable, friendly assistant specializing in the Indian Election Commission and Indian democracy. {lang_instruction}

Your deep expertise covers:
- Voter registration (how to register, update details, check status on voterportal.eci.gov.in)
- Electronic Voting Machines (EVMs) and VVPAT (Voter Verifiable Paper Audit Trail) systems
- Election schedules, phases, counting, and results
- Model Code of Conduct (MCC) — rules and enforcement
- Political parties, candidates, nominations, and campaign rules
- Lok Sabha and Rajya Sabha elections — differences, terms, seats
- State Legislative Assembly (Vidhan Sabha) elections
- Election Commission of India (ECI) — powers, structure, Chief Election Commissioner
- Voting rights, procedures, and the voting process on election day
- NOTA (None of the Above) — what it means and implications
- Postal ballot and proxy voting for NRIs, armed forces, and senior citizens
- Election laws — Representation of the People Act 1951 & 1950
- Delimitation of constituencies
- Election funding, expenditure limits, and affidavit disclosures
- Booth-level officers, returning officers, and election machinery
- Election results and dispute resolution (Election Petitions)

You can also answer ANY general knowledge, science, history, current affairs, or everyday question with equal accuracy.

Formatting rules:
- Use **bold** for key terms and headings
- Use bullet points for lists
- Keep answers clear, structured, and appropriately detailed
- For step-by-step processes, number the steps
- Be concise but thorough — never vague"""

# ---------------- AI RESPONSE ----------------
def get_ai_response(user_input, api_key, language):
    if not api_key:
        return "⚠️ Please enter your Anthropic API key in the sidebar to use this assistant."

    try:
        client = anthropic.Anthropic(api_key=api_key)

        # Add user message to API history
        st.session_state.api_messages.append({
            "role": "user",
            "content": user_input
        })

        # Keep last 20 messages for context
        messages_to_send = st.session_state.api_messages[-20:]

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=get_system_prompt(language),
            messages=messages_to_send
        )

        reply = response.content[0].text

        # Add assistant reply to API history
        st.session_state.api_messages.append({
            "role": "assistant",
            "content": reply
        })

        # Keep API history trimmed
        if len(st.session_state.api_messages) > 40:
            st.session_state.api_messages = st.session_state.api_messages[-40:]

        return reply

    except anthropic.AuthenticationError:
        return "⚠️ Invalid API key. Please check your Anthropic API key in the sidebar."
    except anthropic.RateLimitError:
        return "⚠️ Rate limit reached. Please wait a moment and try again."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ---------------- DISPLAY CHAT ----------------
chat_container = st.container()

with chat_container:
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align:center; padding: 40px 20px; color: #888;">
            <div style="font-size: 48px; margin-bottom: 12px;">🇮🇳</div>
            <div style="font-size: 16px; font-weight: 500; color: #444; margin-bottom: 8px;">Welcome to Election Assistant</div>
            <div style="font-size: 13px; line-height: 1.7; max-width: 400px; margin: 0 auto;">
                Ask me anything about Indian elections — voter registration, EVMs, 
                election laws, or any general question. Use the quick questions 
                in the sidebar or type below.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(f"""
                <div class="user-msg-wrap">
                    <div class="user-msg">👤 {msg}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bot-msg-wrap">
                    <div class="bot-avatar">EC</div>
                    <div class="bot-msg">{msg}</div>
                </div>
                """, unsafe_allow_html=True)

# ---------------- INPUT ----------------
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([9, 1])

with col1:
    default_val = st.session_state.pending_input
    user_input = st.text_input(
        "Ask your question",
        value=default_val,
        placeholder="Ask about elections or anything else...",
        label_visibility="collapsed",
        key="main_input"
    )

with col2:
    send = st.button("Send ↗", use_container_width=True)

# Clear pending input
if st.session_state.pending_input:
    st.session_state.pending_input = ""

# ---------------- HANDLE SEND ----------------
if (send or user_input) and user_input.strip():
    st.session_state.chat_history.append(("user", user_input.strip()))

    with st.spinner("🤖 Thinking..."):
        response = get_ai_response(user_input.strip(), api_key, language)

    st.session_state.chat_history.append(("bot", response))

    # Keep display history to last 30 messages
    if len(st.session_state.chat_history) > 30:
        st.session_state.chat_history = st.session_state.chat_history[-30:]

    st.rerun()
