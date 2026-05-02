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
st.caption("AI-powered retrieval + reasoning system")

# ---------------- SETTINGS ----------------
language = st.sidebar.selectbox("🌐 Language", ["English", "Tamil"])

if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.chat = []

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

# ---------------- STEP 1: UNDERSTAND QUERY ----------------
def analyze_query(query):
    try:
        prompt = f"""
        Analyze the user question and extract:

        - Intent
        - Key topics
        - Expected answer type (steps / explanation / definition)

        Question: {query}
        """
        res = model.generate_content(prompt)
        return res.text if res else query
    except:
        return query

# ---------------- STEP 2: RETRIEVE DATA ----------------
def retrieve_data(query):
    try:
        # Add India context for better relevance
        search_query = query + " India election"

        summary = wikipedia.summary(search_query, sentences=5)
        return summary
    except:
        return None

# ---------------- STEP 3: STRUCTURED AI RESPONSE ----------------
def generate_structured_answer(query, context):
    try:
        prompt = f"""
        You are an expert Election Assistant.

        Use the following context to answer the question.

        Provide:
        - Clear explanation
        - Step-by-step (if applicable)
        - Focus on Indian system

        Question: {query}

        Context:
        {context}
        """
        res = model.generate_content(prompt)
        return res.text if res else None
    except:
        return None

# ---------------- MAIN PIPELINE ----------------
def rag_pipeline(query):

    # Step 1: Understand
    analyzed = analyze_query(query)

    # Step 2: Retrieve
    data = retrieve_data(query)

    # Step 3: Generate answer
    if data:
        answer = generate_structured_answer(query, data)
        if answer:
            return answer

    # fallback to direct AI
    try:
        fallback = model.generate_content(query)
        if fallback and fallback.text:
            return fallback.text
    except:
        pass

    return "⚠️ Unable to generate answer."

# ---------------- INPUT ----------------
user_input = st.text_input("💬 Ask your question:")

# ---------------- RESPONSE ----------------
if user_input:
    st.session_state.chat.append(("user", user_input))

    placeholder = st.empty()
    placeholder.markdown("🤖 Thinking...")
    time.sleep(1)

    response = rag_pipeline(user_input)
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
