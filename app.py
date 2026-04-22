import streamlit as st
import matplotlib.pyplot as plt
import google.generativeai as genai
from deep_translator import GoogleTranslator

# Gemini
genai.configure(api_key="AIzaSyBTAZG3YTiLzOaz-qT2OHbSwOXIUf5rHqU")
model = genai.GenerativeModel("gemini-pro")

st.set_page_config(page_title="Election Assistant", layout="wide")

st.title("🗳 AI Election Assistant")

# ---------------- SETTINGS ----------------
language = st.sidebar.selectbox("🌐 Language", ["English", "Tamil"])
mode = st.sidebar.selectbox("🎯 Mode", ["General User", "First-Time Voter"])

# ---------------- TRANSLATE ----------------
def translate_text(text):
    try:
        if language == "Tamil":
            return GoogleTranslator(source='auto', target='ta').translate(text)
        return text
    except:
        return text

# ---------------- INTENT ----------------
def detect_intent(q):
    q = q.lower()
    if "register" in q:
        return "registration"
    elif "vote" in q:
        return "voting"
    elif "date" in q or "timeline" in q:
        return "timeline"
    elif "eligibility" in q or "age" in q:
        return "eligibility"
    return "general"

# ---------------- DOMAIN CHECK ----------------
def is_election_related(q):
    keywords = ["election", "vote", "voter", "registration", "booth"]
    return any(k in q.lower() for k in keywords)

# ---------------- STATIC KNOWLEDGE (IMPORTANT 🔥) ----------------
def fallback_response(intent):
    if intent == "timeline":
        return """📊 Tamil Nadu Election Timeline 2026:
- Nomination: March 30
- Last Date: April 6
- Scrutiny: April 7
- Withdrawal: April 9
- Voting: April 23
- Counting: May 4"""

    elif intent == "eligibility":
        return "🧾 Eligibility: You must be 18+ years and have a valid voter ID."

    elif intent == "registration":
        return "📝 Register via NVSP website using Form 6 and ID proof."

    elif intent == "voting":
        return "🗳 Go to polling booth, verify ID, and cast your vote."

    return "Ask about voting, registration, timeline, or eligibility."

# ---------------- FIRST TIME MODE ----------------
def first_time_mode(intent):
    if intent == "timeline":
        return "📊 First-time voter: Elections happen in stages like nomination, voting, and counting."
    elif intent == "voting":
        return "🗳 Carry your ID and follow instructions at booth."
    return "👋 As a first-time voter, learn the process and vote responsibly."

# ---------------- AI RESPONSE ----------------
def get_response(user_input):
    if not is_election_related(user_input):
        return "⚠️ I only answer election-related questions."

    intent = detect_intent(user_input)

    # First-time voter mode
    if mode == "First-Time Voter":
        return first_time_mode(intent)

    # Try Gemini
    try:
        prompt = f"""
        You are an election assistant. Answer only about elections in India.
        Question: {user_input}
        """
        res = model.generate_content(prompt)
        if res.text:
            return res.text
    except:
        pass

    # Fallback (VERY IMPORTANT)
    return fallback_response(intent)

# ---------------- CHAT ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

user_input = st.text_input("Ask your question:")

if user_input:
    response = get_response(user_input)
    translated = translate_text(response)

    st.session_state.chat.append(("user", user_input))
    st.session_state.chat.append(("bot", translated))

# Display chat
for role, msg in st.session_state.chat:
    if role == "user":
        st.success("👤 " + msg)
    else:
        st.error("🤖 " + msg)

# ---------------- TIMELINE GRAPH ----------------
if st.button("📊 Show Timeline"):
    steps = ["Nomination", "Scrutiny", "Voting", "Counting"]
    values = [1, 2, 3, 4]

    plt.figure()
    plt.plot(steps, values)
    plt.title("Tamil Nadu Election Timeline 2026")
    st.pyplot(plt)

# ---------------- GOOGLE MAP ----------------
st.subheader("📍 Sample Polling Location")

st.markdown("""
[📍 Chennai Polling Booth (Example)](https://www.google.com/maps/place/Chennai)
""")
