import streamlit as st
import matplotlib.pyplot as plt
import google.generativeai as genai

# Safe import for voice (won’t crash if unavailable)
try:
    import speech_recognition as sr
    voice_available = True
except:
    voice_available = False

# Translator (FIXED VERSION)
from deep_translator import GoogleTranslator

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key="AIzaSyBTAZG3YTiLzOaz-qT2OHbSwOXIUf5rHqU")
model = genai.GenerativeModel("gemini-pro")

# ---------------- UI ----------------
st.set_page_config(page_title="Election Assistant", layout="wide")

st.markdown("""
<style>
.chat-box {
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.user {background-color: #d1e7dd;}
.bot {background-color: #f8d7da;}
</style>
""", unsafe_allow_html=True)

st.title("🗳 AI Election Assistant")
st.caption("Smart guide for election process")

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Settings")

language = st.sidebar.selectbox("🌐 Language", ["English", "Tamil", "Hindi"])
mode = st.sidebar.selectbox("🎯 Mode", ["General User", "First-Time Voter"])

# ---------------- TRANSLATION ----------------
def translate_text(text):
    try:
        if language == "Tamil":
            return GoogleTranslator(source='auto', target='ta').translate(text)
        elif language == "Hindi":
            return GoogleTranslator(source='auto', target='hi').translate(text)
        return text
    except:
        return text

# ---------------- INTENT DETECTION ----------------
def detect_intent(query):
    q = query.lower()

    if any(w in q for w in ["register", "signup", "enroll"]):
        return "registration"
    elif any(w in q for w in ["vote", "voting", "poll"]):
        return "voting"
    elif any(w in q for w in ["timeline", "process", "steps"]):
        return "timeline"
    elif any(w in q for w in ["id", "document"]):
        return "id"
    else:
        return "general"

# ---------------- DOMAIN FILTER ----------------
def is_election_related(query):
    keywords = [
        "election", "vote", "voter", "registration",
        "poll", "booth", "candidate", "ballot", "campaign"
    ]
    return any(word in query.lower() for word in keywords)

# ---------------- FIRST-TIME VOTER MODE ----------------
def first_time_guidance(intent):
    if intent == "registration":
        return "📝 Register on NVSP website and keep documents ready."
    elif intent == "voting":
        return "🗳 Visit polling booth, carry ID, and follow instructions."
    elif intent == "id":
        return "📄 Carry Aadhaar, Voter ID, or Passport."
    elif intent == "timeline":
        return "📊 Announcement → Campaign → Voting → Counting → Results."
    else:
        return "👋 As a first-time voter, learn the process and carry valid ID."

# ---------------- GEMINI RESPONSE ----------------
def get_ai_response(user_input):
    if not is_election_related(user_input):
        return "⚠️ I only answer election-related questions."

    intent = detect_intent(user_input)

    if mode == "First-Time Voter":
        return first_time_guidance(intent)

    prompt = f"""
    You are an Election Assistant.

    Rules:
    - Answer ONLY election-related questions
    - Keep answers simple and clear
    - Focus on Indian election system

    Intent: {intent}
    Question: {user_input}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "AI error. Try again."

# ---------------- CHAT MEMORY ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------------- LAYOUT ----------------
col1, col2 = st.columns([2, 1])

# ---------------- CHAT ----------------
with col1:
    st.subheader("💬 Chat Assistant")

    user_input = st.text_input("Ask your question:")

    if user_input:
        response = get_ai_response(user_input)
        translated = translate_text(response)

        st.session_state.chat.append(("user", user_input))
        st.session_state.chat.append(("bot", translated))

    for role, msg in st.session_state.chat:
        if role == "user":
            st.markdown(f'<div class="chat-box user">👤 {msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-box bot">🤖 {msg}</div>', unsafe_allow_html=True)

# ---------------- RIGHT PANEL ----------------
with col2:
    st.subheader("🎤 Voice Input")

    if voice_available:
        if st.button("Speak"):
            r = sr.Recognizer()
            try:
                with sr.Microphone() as source:
                    st.info("Listening...")
                    audio = r.listen(source)

                text = r.recognize_google(audio)
                st.success(f"You said: {text}")

                response = get_ai_response(text)
                st.write(translate_text(response))

            except:
                st.error("Voice recognition failed")
    else:
        st.info("Voice input not supported in deployment.")

    # ---------------- TIMELINE ----------------
    st.subheader("📊 Election Timeline")

    if st.button("Show Timeline"):
        steps = ["Announcement", "Campaign", "Voting", "Counting", "Results"]
        values = [1, 2, 3, 4, 5]

        plt.figure()
        plt.plot(steps, values)
        plt.title("Election Timeline")

        st.pyplot(plt)

    # ---------------- MAP ----------------
    st.subheader("📍 Polling Location")
    st.markdown("[Open Google Maps](https://www.google.com/maps)")
