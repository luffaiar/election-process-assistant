import streamlit as st
import google.generativeai as genai
from deep_translator import GoogleTranslator
import wikipedia
import time
from gtts import gTTS
import tempfile

# ---------------- GEMINI ----------------
genai.configure(api_key="AIzaSyBTAZG3YTiLzOaz-qT2OHbSwOXIUf5rHqU")
model = genai.GenerativeModel("gemini-pro")

# ---------------- UI ----------------
st.set_page_config(page_title="Election Assistant GPT", layout="wide")

# ---------------- CSS (Responsive + Clean) ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom, #ffffff, #f5f7fa);
}

/* Header */
.header {
    text-align:center;
    padding:12px;
    border-radius:10px;
    background: linear-gradient(to right, #ff9933, #ffffff, #138808);
    font-size:20px;
    font-weight:bold;
}

/* Chat bubbles */
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

/* Mobile responsive */
@media (max-width: 768px) {
    .user-msg, .bot-msg {
        max-width: 100% !important;
        font-size: 14px;
    }
}

/* Typing dots */
.typing {
    display: inline-block;
}
.typing span {
    animation: blink 1.4s infinite both;
}
.typing span:nth-child(2) {
    animation-delay: .2s;
}
.typing span:nth-child(3) {
    animation-delay: .4s;
}
@keyframes blink {
    0% {opacity: .2;}
    20% {opacity: 1;}
    100% {opacity: .2;}
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="header">🗳 Election Commission Assistant</div>', unsafe_allow_html=True)
st.caption("🇮🇳 AI for Elections & Indian Politics")

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

# ---------------- VOICE OUTPUT ----------------
def generate_voice(text):
    try:
        tts = gTTS(text=text, lang='ta' if language == "Tamil" else 'en')
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp.name)
        return tmp.name
    except:
        return None

# ---------------- SMART RESPONSES ----------------
def smart_response(q):
    q = q.lower()

    if "document" in q:
        return "📄 Aadhaar, Voter ID, Passport, Address Proof"

    if "voting process" in q:
        return "🗳 Check list → Visit booth → Verify ID → Vote"

    if "register" in q:
        return "📝 Register at https://www.nvsp.in using Form 6"

    return None

# ---------------- CM ----------------
def get_cm_info(q):
    cm = {
        "tamil nadu": "M.K. Stalin",
        "karnataka": "Siddaramaiah"
    }
    for state in cm:
        if state in q.lower():
            return f"🏛 CM of {state.title()}: {cm[state]}"
    return None

# ---------------- POLITICAL ----------------
def political_knowledge(q):
    q = q.lower()

    if "prime minister" in q:
        return "🇮🇳 Narendra Modi is the Prime Minister of India"

    if "nda" in q:
        return "🟠 NDA is BJP-led alliance"

    if "india alliance" in q:
        return "🔵 INDIA is opposition alliance"

    return None

# ---------------- WEB ----------------
def web_search(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except:
        return None

# ---------------- AI ----------------
def get_ai_response(user_input):

    for func in [smart_response, get_cm_info, political_knowledge]:
        res = func(user_input)
        if res:
            return res

    try:
        res = model.generate_content(user_input)
        if res and res.text:
            return res.text
    except:
        pass

    web = web_search(user_input)
    if web:
        return "🌐 " + web

    return "⚠️ Ask election-related questions"

# ---------------- SUGGESTIONS ----------------
st.subheader("💡 Suggested")

suggestions = ["PM of India?", "CM of Tamil Nadu?", "Voting process"]

cols = st.columns(3)
selected = None

for i, q in enumerate(suggestions):
    if cols[i].button(q):
        selected = q

# ---------------- INPUT ----------------
user_input = st.text_input("💬 Ask your question:")

if selected:
    user_input = selected

# ---------------- RESPONSE ----------------
if user_input:
    st.session_state.chat.append(("user", user_input))

    # Typing animation
    placeholder = st.empty()
    placeholder.markdown(
        '<div class="bot-msg">🤖 <span class="typing"><span>.</span><span>.</span><span>.</span></span></div>',
        unsafe_allow_html=True
    )

    time.sleep(1.2)

    response = get_ai_response(user_input)
    translated = translate_text(response)

    placeholder.empty()

    st.session_state.chat.append(("bot", translated))

# ---------------- LIMIT HISTORY ----------------
if len(st.session_state.chat) > 8:
    st.session_state.chat = st.session_state.chat[-8:]

# ---------------- DISPLAY ----------------
for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f'<div class="user-msg">👤 {msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">🤖 {msg}</div>', unsafe_allow_html=True)

        # Voice button
        audio = generate_voice(msg)
        if audio:
            st.audio(audio)

# ---------------- AUTO SCROLL ----------------
st.markdown("""
<script>
window.scrollTo(0, document.body.scrollHeight);
</script>
""", unsafe_allow_html=True)
