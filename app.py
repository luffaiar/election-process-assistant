import streamlit as st
import google.generativeai as genai
import wikipedia
from deep_translator import GoogleTranslator
import time

# ---------------- CONFIG ----------------
genai.configure(api_key="AIzaSyDNDy21ZlSFAPkjRvRdgPfPb1bsjwxafBE")
model = genai.GenerativeModel("gemini-pro")

st.set_page_config(page_title="Election AI Assistant", layout="wide")

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp { background: linear-gradient(to bottom, #ffffff, #eef2f7); }

.header {
    text-align:center;
    padding:15px;
    border-radius:10px;
    background: linear-gradient(to right, #ff9933, #ffffff, #138808);
    font-size:22px;
    font-weight:bold;
}

.user-msg {
    background:#e8f5e9;
    padding:10px;
    border-radius:12px;
    margin:6px 0;
    text-align:right;
    max-width:75%;
    margin-left:auto;
}

.bot-msg {
    background:#f1f3f4;
    padding:12px;
    border-radius:12px;
    margin:6px 0;
    text-align:left;
    max-width:75%;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">🗳 Indian Election AI Assistant</div>', unsafe_allow_html=True)
st.caption("AI that understands, searches, and explains")

# ---------------- SETTINGS ----------------
language = st.sidebar.selectbox("🌐 Language", ["English", "Tamil"])

if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.chat = []

# ---------------- SESSION ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------------- TRANSLATION ----------------
def translate(text):
    try:
        if language == "Tamil":
            return GoogleTranslator(source='auto', target='ta').translate(text)
        return text
    except:
        return text

# ---------------- GEMINI PRIMARY ----------------
def gemini_answer(query):
    try:
        prompt = f"""
        You are an advanced AI assistant.

        RULES:
        - Answer any question clearly
        - If election-related → focus on Indian system
        - Provide structured explanation
        - Use steps if needed

        Question: {query}
        """

        res = model.generate_content(prompt)

        if res and res.text and len(res.text) > 40:
            return res.text
    except:
        pass

    return None

# ---------------- WIKI FETCH ----------------
def fetch_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=5)
    except:
        return None

# ---------------- AI SUMMARIZER ----------------
def summarize_with_ai(text, query):
    try:
        prompt = f"""
        Summarize the following information clearly and correctly.

        Make it:
        - Structured
        - Easy to understand
        - Relevant to the question

        Question: {query}

        Content:
        {text}
        """
        res = model.generate_content(prompt)

        if res and res.text:
            return res.text
    except:
        pass

    return text

# ---------------- MAIN PIPELINE ----------------
def generate_response(query):

    # 1️⃣ Gemini first
    ai = gemini_answer(query)
    if ai:
        return ai

    # 2️⃣ Wikipedia fetch
    wiki = fetch_wikipedia(query)
    if wiki:
        summarized = summarize_with_ai(wiki, query)
        return f"🌐 Based on online sources:\n\n{summarized}"

    return "⚠️ Sorry, I couldn't find a proper answer."

# ---------------- INPUT ----------------
user_input = st.text_input("💬 Ask your question:")

# ---------------- RESPONSE ----------------
if user_input:
    st.session_state.chat.append(("user", user_input))

    placeholder = st.empty()
    placeholder.markdown("🤖 Thinking...")
    time.sleep(1)

    response = generate_response(user_input)
    translated = translate(response)

    placeholder.empty()

    st.session_state.chat.append(("bot", translated))

# ---------------- LIMIT HISTORY ----------------
if len(st.session_state.chat) > 10:
    st.session_state.chat = st.session_state.chat[-10:]

# ---------------- DISPLAY ----------------
st.subheader("💬 Conversation")

for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f'<div class="user-msg">👤 {msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">🤖 {msg}</div>', unsafe_allow_html=True)

# ---------------- AUTO SCROLL ----------------
st.markdown("""
<script>
window.scrollTo(0, document.body.scrollHeight);
</script>
""", unsafe_allow_html=True)
