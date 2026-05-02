import streamlit as st
import google.generativeai as genai
import wikipedia
import time

# ---------------- CONFIG ----------------
genai.configure(api_key="AIzaSyDNDy21ZlSFAPkjRvRdgPfPb1bsjwxafBE")
model = genai.GenerativeModel("gemini-pro")

st.set_page_config(page_title="Indian Election AI Assistant", layout="wide")

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
st.caption("GPT-style assistant with election awareness")

# ---------------- SESSION ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.chat = []

# ---------------- GREETING HANDLER ----------------
def handle_greeting(text):
    greetings = ["hi", "hello", "hey", "good morning", "good evening"]
    if text.lower().strip() in greetings:
        return "👋 Hello! I’m your AI assistant. You can ask me anything, especially about Indian elections, voting process, and politics."
    return None

# ---------------- GEMINI RESPONSE ----------------
def gemini_answer(query):
    try:
        prompt = f"""
        You are a helpful AI assistant.

        - Answer any question naturally like ChatGPT
        - If the question is about elections, focus on Indian election system
        - Give clear, structured answers when needed

        Question: {query}
        """

        res = model.generate_content(prompt)

        if res and res.text:
            return res.text
    except:
        return None

# ---------------- WIKIPEDIA FALLBACK ----------------
def wiki_answer(query):
    try:
        return wikipedia.summary(query + " India", sentences=3)
    except:
        return None

# ---------------- MAIN PIPELINE ----------------
def generate_response(user_input):

    # 1️⃣ Greeting
    greet = handle_greeting(user_input)
    if greet:
        return greet

    # 2️⃣ Gemini (Primary)
    ai = gemini_answer(user_input)
    if ai:
        return ai

    # 3️⃣ Wikipedia fallback
    wiki = wiki_answer(user_input)
    if wiki:
        return f"🌐 {wiki}"

    # 4️⃣ Final fallback (NEVER FAIL)
    return "🤖 I'm here to help! Could you please rephrase your question?"

# ---------------- INPUT ----------------
user_input = st.text_input("💬 Ask your question:")

# ---------------- RESPONSE ----------------
if user_input:
    st.session_state.chat.append(("user", user_input))

    placeholder = st.empty()
    placeholder.markdown("🤖 Thinking...")
    time.sleep(1)

    response = generate_response(user_input)

    placeholder.empty()

    st.session_state.chat.append(("bot", response))

# ---------------- LIMIT CHAT ----------------
if len(st.session_state.chat) > 12:
    st.session_state.chat = st.session_state.chat[-12:]

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
