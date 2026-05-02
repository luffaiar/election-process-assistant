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
.stApp {
    background: linear-gradient(to bottom, #ffffff, #eef2f7);
}

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
st.caption("AI-powered assistant for elections, governance, and general knowledge")

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

# ---------------- WIKIPEDIA FALLBACK ----------------
def wiki_fallback(query):
    try:
        summary = wikipedia.summary(query + " India", sentences=3)
        return f"🌐 **Additional Info:**\n{summary}"
    except:
        return None

# ---------------- GEMINI RESPONSE ----------------
def get_ai_response(user_input):
    try:
        prompt = f"""
        You are an intelligent AI assistant.

        PRIORITY:
        - If the question is about elections, focus on the Indian election system.
        - Provide detailed, structured answers.
        - Explain processes step-by-step where needed.

        You can also answer general knowledge questions.

        Question: {user_input}
        """

        res = model.generate_content(prompt)

        if res and res.text and len(res.text) > 20:
            return res.text

    except:
        pass

    return None

# ---------------- MAIN RESPONSE PIPELINE ----------------
def generate_response(user_input):

    # Step 1: AI
    ai_answer = get_ai_response(user_input)

    if ai_answer:
        return ai_answer

    # Step 2: Wikipedia fallback
    wiki = wiki_fallback(user_input)
    if wiki:
        return wiki

    return "⚠️ Sorry, I couldn't find a reliable answer. Please rephrase your question."

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
