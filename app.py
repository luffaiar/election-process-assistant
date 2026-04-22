import streamlit as st
import google.generativeai as genai
from deep_translator import GoogleTranslator
import time

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key="AIzaSyBTAZG3YTiLzOaz-qT2OHbSwOXIUf5rHqU")
model = genai.GenerativeModel("gemini-pro")

# ---------------- UI ----------------
st.set_page_config(page_title="Election Assistant GPT", layout="centered")

st.markdown("""
<style>
.chat-bubble-user {
    background-color: #d1e7dd;
    padding: 10px;
    border-radius: 10px;
    margin: 5px 0;
}
.chat-bubble-bot {
    background-color: #f1f3f4;
    padding: 10px;
    border-radius: 10px;
    margin: 5px 0;
}
button {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🗳 Election Assistant GPT")
st.caption("Smart personalized assistant for voter guidance")

# ---------------- SIDEBAR ----------------
st.sidebar.title("👤 User Category")

user_type = st.sidebar.selectbox(
    "Select your category:",
    ["General (20–50)", "New Voter (18+)", "Senior Citizen (60+)"]
)

language = st.sidebar.selectbox("🌐 Language", ["English", "Tamil"])

# ---------------- TRANSLATION ----------------
def translate_text(text):
    try:
        if language == "Tamil":
            return GoogleTranslator(source='auto', target='ta').translate(text)
        return text
    except:
        return text

# ---------------- DOMAIN CHECK ----------------
def is_election_related(query):
    keywords = [
        "election", "vote", "voter", "registration",
        "id", "booth", "poll", "eligibility"
    ]
    return any(k in query.lower() for k in keywords)

# ---------------- PERSONALIZED GUIDE ----------------
def get_personalized_context():
    if user_type == "New Voter (18+)":
        return "Focus on explaining registration and first-time voting steps."
    elif user_type == "Senior Citizen (60+)":
        return "Focus on assistance, easy voting, and senior support."
    return "General voter guidance and awareness."

# ---------------- AI RESPONSE ----------------
def get_ai_response(user_input):
    if not is_election_related(user_input):
        return "⚠️ I only answer election-related questions."

    prompt = f"""
    You are an intelligent Election Assistant GPT.

    User Category: {user_type}

    Context:
    {get_personalized_context()}

    Rules:
    - Give clear, short, and relevant answers
    - Do NOT repeat the same content
    - Adapt answer based on the question

    Question: {user_input}
    """

    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
    except:
        pass

    return "⚠️ Unable to generate response. Try again."

# ---------------- CHAT MEMORY ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------------- SUGGESTED QUESTIONS ----------------
st.subheader("💡 Try asking:")

col1, col2, col3 = st.columns(3)

suggestions = [
    "What is election?",
    "How to register for voter ID?",
    "Who is eligible to vote?",
    "What is voting process?",
    "What documents are needed?",
    "How senior citizens can vote?"
]

selected_question = None

for i, q in enumerate(suggestions):
    if st.button(q, key=f"btn_{i}"):
        selected_question = q

# ---------------- INPUT ----------------
user_input = st.text_input("💬 Ask your question:")

if selected_question:
    user_input = selected_question

# ---------------- RESPONSE ----------------
if user_input:
    st.session_state.chat.append(("user", user_input))

    # Typing animation
    placeholder = st.empty()
    placeholder.markdown("🤖 Typing...")

    time.sleep(1)

    response = get_ai_response(user_input)
    translated = translate_text(response)

    placeholder.empty()

    st.session_state.chat.append(("bot", translated))

# ---------------- DISPLAY CHAT ----------------
for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f'<div class="chat-bubble-user">👤 {msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-bot">🤖 {msg}</div>', unsafe_allow_html=True)
