import streamlit as st
import google.generativeai as genai
from deep_translator import GoogleTranslator

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key="AIzaSyBTAZG3YTiLzOaz-qT2OHbSwOXIUf5rHqU")
model = genai.GenerativeModel("gemini-pro")

# ---------------- UI ----------------
st.set_page_config(page_title="Election Assistant GPT", layout="centered")

st.title("🗳 Election Assistant GPT")
st.caption("Personalized AI assistant for voter guidance")

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

# ---------------- PERSONALIZED GUIDANCE ----------------
def get_personalized_guidance(user_type):
    if user_type == "New Voter (18+)":
        return """🆕 First-Time Voter Guide:
- Register using Form 6 on NVSP website
- Keep Aadhaar/ID proof ready
- Check your name in voter list
- Visit polling booth on election day
- Follow instructions and vote confidently"""

    elif user_type == "Senior Citizen (60+)":
        return """👴 Senior Citizen Support:
- Option for postal ballot (if eligible)
- Assistance available at polling booths
- Avoid long queues (priority given)
- Carry valid ID
- Seek help from officials if needed"""

    else:
        return """👤 General Voter Guide:
- Verify voter ID before election
- Know your polling booth
- Follow election rules
- Avoid fake news
- Vote responsibly"""

# ---------------- VOTER ID ENROLLMENT (COMMON FOR ALL) ----------------
def voter_id_info():
    return """📝 Voter ID Enrollment:
1. Visit https://www.nvsp.in
2. Fill Form 6 (New Registration)
3. Upload ID and address proof
4. Submit application
5. Track status online"""

# ---------------- AI RESPONSE ----------------
def get_ai_response(user_input):
    if not is_election_related(user_input):
        return "⚠️ I only answer election-related questions."

    base_guide = get_personalized_guidance(user_type)
    enrollment = voter_id_info()

    prompt = f"""
    You are an Election Assistant GPT.

    User Category: {user_type}

    Instructions:
    - Answer only election-related questions
    - Provide clear and simple answers
    - Include helpful guidance based on user category
    - Mention voter ID enrollment steps if relevant

    User Question: {user_input}

    Additional Context:
    {base_guide}

    Voter ID Info:
    {enrollment}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        # fallback
        return base_guide + "\n\n" + enrollment

# ---------------- CHAT ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

user_input = st.text_input("💬 Ask your question:")

if user_input:
    response = get_ai_response(user_input)
    translated = translate_text(response)

    st.session_state.chat.append(("user", user_input))
    st.session_state.chat.append(("bot", translated))

# ---------------- DISPLAY CHAT ----------------
for role, msg in st.session_state.chat:
    if role == "user":
        st.success("👤 " + msg)
    else:
        st.info("🤖 " + msg)
