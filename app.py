import streamlit as st
import google.generativeai as genai
from deep_translator import GoogleTranslator
import time

# ---------------- GEMINI ----------------
genai.configure(api_key="AIzaSyBTAZG3YTiLzOaz-qT2OHbSwOXIUf5rHqU")
model = genai.GenerativeModel("gemini-pro")

# ---------------- UI ----------------
st.set_page_config(page_title="Election Assistant GPT", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom, #ffffff, #f5f7fa);
}

.header {
    text-align:center;
    padding:12px;
    border-radius:10px;
    background: linear-gradient(to right, #ff9933, #ffffff, #138808);
    font-size:20px;
    font-weight:bold;
}

.user-msg {
    background:#e8f5e9;
    padding:10px;
    border-radius:12px;
    margin:6px 0;
    text-align:right;
    max-width:80%;
    margin-left:auto;
}

.bot-msg {
    background:#f1f3f4;
    padding:10px;
    border-radius:12px;
    margin:6px 0;
    text-align:left;
    max-width:80%;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="header">🗳 Election Commission Assistant</div>', unsafe_allow_html=True)
st.caption("🇮🇳 AI-powered Election Guidance System")

# ---------------- SETTINGS ----------------
language = st.sidebar.selectbox("🌐 Language", ["English", "Tamil"])

if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.chat = []

# ---------------- SESSION ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------------- TRANSLATION ----------------
def translate_text(text):
    try:
        if language == "Tamil":
            return GoogleTranslator(source='auto', target='ta').translate(text)
        return text
    except:
        return text

# ---------------- AI RESPONSE ----------------
def get_ai_response(user_input):

    try:
        prompt = f"""
        You are an intelligent assistant.

        PRIORITY:
        - If the question is about elections, give detailed explanation based on Indian election system.
        - Provide step-by-step guidance when possible.
        - Keep answers structured and easy to understand.

        You can also answer general questions if asked.

        Question: {user_input}
        """

        response = model.generate_content(prompt)

        if response and response.text:
            return response.text

    except:
        pass

    return "⚠️ Unable to generate response. Please try again."

# ---------------- INPUT ----------------
user_input = st.text_input("💬 Ask your question:")

# ---------------- RESPONSE ----------------
if user_input:
    st.session_state.chat.append(("user", user_input))

    placeholder = st.empty()
    placeholder.markdown("🤖 Thinking...")
    time.sleep(1)

    response = get_ai_response(user_input)
    translated = translate_text(response)

    placeholder.empty()

    st.session_state.chat.append(("bot", translated))

# ---------------- LIMIT CHAT ----------------
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
