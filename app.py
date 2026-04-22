import streamlit as st
import google.generativeai as genai
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile
import time

# ---------------- GEMINI ----------------
genai.configure(api_key="AIzaSyBTAZG3YTiLzOaz-qT2OHbSwOXIUf5rHqU")
model = genai.GenerativeModel("gemini-pro")

# ---------------- UI ----------------
st.set_page_config(page_title="Election Assistant GPT", layout="wide")

st.title("🗳 Election Assistant GPT")
st.caption("🇮🇳 Smart AI for voter awareness")

# ---------------- SIDEBAR ----------------
st.sidebar.title("📂 Navigation")

page = st.sidebar.radio("Go to", ["💬 Chat", "📜 History"])

user_type = st.sidebar.selectbox(
    "👤 Category",
    ["General (20–50)", "New Voter (18+)", "Senior Citizen (60+)"]
)

language = st.sidebar.selectbox("🌐 Language", ["English", "Tamil"])

# ---------------- SESSION STORAGE ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------------- TRANSLATE ----------------
def translate_text(text):
    try:
        if language == "Tamil":
            return GoogleTranslator(source='auto', target='ta').translate(text)
        return text
    except:
        return text

# ---------------- VOICE (Tamil Output) ----------------
def speak_tamil(text):
    try:
        tts = gTTS(text=text, lang='ta')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except:
        return None

# ---------------- SMART RESPONSES ----------------
def smart_response(q):
    q = q.lower()

    if "document" in q or "id" in q:
        return "📄 Documents: Aadhaar, Voter ID, Passport, Address Proof"

    elif "process" in q or "vote" in q:
        return "🗳 Voting: Check list → Go booth → Verify ID → Vote"

    elif "eligibility" in q:
        return "🧾 Must be 18+ and registered voter"

    elif "senior" in q:
        return "👴 Seniors get priority, assistance & postal ballot option"

    elif "register" in q:
        return "📝 Register at https://www.nvsp.in using Form 6"

    elif "election" in q:
        return "🗳 Election is the process of choosing leaders by voting"

    return None

# ---------------- AI ----------------
def get_ai_response(user_input):

    # Step 1: Smart answer
    smart = smart_response(user_input)
    if smart:
        return smart

    # Step 2: Gemini
    try:
        prompt = f"""
        You are Election Assistant GPT.

        User Type: {user_type}

        Give clear and useful answer.

        Question: {user_input}
        """
        res = model.generate_content(prompt)

        if res and res.text:
            return res.text
    except:
        pass

    return "⚠️ Please ask election-related questions."

# ================= PAGE 1: CHAT =================
if page == "💬 Chat":

    st.subheader("💡 Quick Questions")

    col1, col2, col3 = st.columns(3)

    suggestions = [
        "What documents are needed?",
        "Voting process",
        "Eligibility",
        "How to register?",
        "Senior citizen voting",
        "What is election?"
    ]

    selected = None
    for i, q in enumerate(suggestions):
        if st.button(q, key=f"sugg_{i}"):
            selected = q

    user_input = st.text_input("💬 Ask your question:")

    if selected:
        user_input = selected

    if user_input:
        st.session_state.chat.append(("user", user_input))

        placeholder = st.empty()
        placeholder.markdown("🤖 Typing...")

        time.sleep(1)

        response = get_ai_response(user_input)
        translated = translate_text(response)

        placeholder.empty()

        st.session_state.chat.append(("bot", translated))

        # 🔊 Tamil Voice Output
        if language == "Tamil":
            audio_file = speak_tamil(translated)
            if audio_file:
                st.audio(audio_file)

    # Display chat
    for role, msg in st.session_state.chat:
        if role == "user":
            st.markdown(f"🧑 **You:** {msg}")
        else:
            st.markdown(f"🤖 **Assistant:** {msg}")

# ================= PAGE 2: HISTORY =================
elif page == "📜 History":

    st.subheader("📜 Previous Questions & Answers")

    if not st.session_state.chat:
        st.info("No history yet.")
    else:
        for i in range(0, len(st.session_state.chat), 2):
            try:
                user_q = st.session_state.chat[i][1]
                bot_a = st.session_state.chat[i+1][1]

                st.markdown(f"""
                ### 🧑 {user_q}
                ➤ 🤖 {bot_a}
                ---
                """)
            except:
                pass
