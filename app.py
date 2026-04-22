import streamlit as st
import google.generativeai as genai
from deep_translator import GoogleTranslator
import wikipedia
import time

# ---------------- GEMINI ----------------
genai.configure(api_key="AIzaSyBTAZG3YTiLzOaz-qT2OHbSwOXIUf5rHqU")
model = genai.GenerativeModel("gemini-pro")

# ---------------- UI ----------------
st.set_page_config(page_title="Election Assistant GPT", layout="wide")

# ---------------- CSS THEME ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom, #ffffff, #f5f7fa);
}

.header {
    text-align: center;
    padding: 15px;
    border-radius: 10px;
    background: linear-gradient(to right, #ff9933, #ffffff, #138808);
    font-weight: bold;
    font-size: 22px;
    margin-bottom: 10px;
}

.subheader {
    text-align: center;
    font-size: 14px;
    color: #333;
    margin-bottom: 20px;
}

.user-msg {
    background-color: #e8f5e9;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
    text-align: right;
}

.bot-msg {
    background-color: #f1f3f4;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
    text-align: left;
}

.stButton>button {
    border-radius: 8px;
    background-color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="header">🗳 Election Commission Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">🇮🇳 AI for Elections & Indian Politics</div>', unsafe_allow_html=True)

st.info("📌 Official-style assistant for election awareness and political knowledge")

# ---------------- SETTINGS ----------------
language = st.sidebar.selectbox("🌐 Language", ["English", "Tamil"])

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

# ---------------- SMART RESPONSES ----------------
def smart_response(q):
    q = q.lower()

    if "document" in q or "id" in q:
        return "📄 Documents: Aadhaar, Voter ID, Passport, Address Proof"

    if "voting process" in q:
        return """🗳 Voting Process:
1. Check voter list
2. Visit polling booth
3. Verify identity
4. Cast vote"""

    if "eligibility" in q:
        return "🧾 Must be 18+ and registered voter"

    if "register" in q:
        return "📝 Register at https://www.nvsp.in using Form 6"

    return None

# ---------------- VOTER ID PROCESS ----------------
def voter_id_process(q):
    if "voter id process" in q.lower():
        return """📝 Voter ID Registration:

1. Visit https://www.nvsp.in  
2. Fill Form 6  
3. Upload documents  
4. Submit application  
5. Track status  

✔ Ensure correct details"""

    return None

# ---------------- CM INFO ----------------
def get_cm_info(q):
    q = q.lower()
    cm_data = {
        "tamil nadu": "M.K. Stalin",
        "kerala": "Pinarayi Vijayan",
        "karnataka": "Siddaramaiah",
        "uttar pradesh": "Yogi Adityanath"
    }

    for state in cm_data:
        if state in q:
            return f"🏛 CM of {state.title()}: {cm_data[state]}"
    return None

# ---------------- POLITICAL KNOWLEDGE ----------------
def political_knowledge(q):
    q = q.lower()

    if "prime minister" in q:
        return "🇮🇳 PM of India: Narendra Modi"

    if "president" in q:
        return "🇮🇳 President of India: Droupadi Murmu"

    if "nda" in q:
        return "🟠 NDA: BJP-led alliance"

    if "india alliance" in q:
        return "🔵 INDIA Alliance: Opposition coalition"

    if "constitution" in q:
        return "📜 Indian Constitution is the supreme law (1950)"

    if "election commission" in q:
        return "🏛 Election Commission conducts elections in India"

    return None

# ---------------- PARTY TABLE ----------------
def party_comparison(q):
    if "nda vs india" in q.lower():
        return {
            "table": True,
            "data": [
                ["Alliance", "Type"],
                ["NDA", "Ruling"],
                ["INDIA", "Opposition"]
            ]
        }
    return None

# ---------------- WEB SEARCH ----------------
def web_search_answer(query):
    try:
        return "🌐 " + wikipedia.summary(query, sentences=2)
    except:
        return None

# ---------------- AI RESPONSE ----------------
def get_ai_response(user_input):

    for func in [smart_response, voter_id_process, get_cm_info, political_knowledge, party_comparison]:
        res = func(user_input)
        if res:
            return res

    try:
        prompt = f"""
        You are an Indian Election Assistant.

        Answer clearly and accurately.

        Question: {user_input}
        """
        res = model.generate_content(prompt)

        if res and res.text:
            return res.text
    except:
        pass

    web = web_search_answer(user_input)
    if web:
        return web

    return "⚠️ Please ask election or political questions."

# ---------------- SUGGESTIONS ----------------
st.subheader("💡 Suggested Questions")

suggestions = [
    "Who is PM of India?",
    "CM of Tamil Nadu?",
    "NDA vs INDIA",
    "How to apply voter ID?",
    "Voting process"
]

cols = st.columns(3)
selected = None

for i, q in enumerate(suggestions):
    if cols[i % 3].button(q):
        selected = q

# ---------------- INPUT ----------------
user_input = st.text_input("💬 Ask your question:")

if selected:
    user_input = selected

# ---------------- RESPONSE ----------------
if user_input:
    st.session_state.chat.append(("user", user_input))

    placeholder = st.empty()
    placeholder.markdown("🤖 Typing...")
    time.sleep(1)

    response = get_ai_response(user_input)

    placeholder.empty()

    translated = translate_text(response)

    st.session_state.chat.append(("bot", translated))

# ---------------- CHAT DISPLAY ----------------
st.subheader("💬 Conversation")

for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f'<div class="user-msg">👤 {msg}</div>', unsafe_allow_html=True)
    else:
        if isinstance(msg, dict) and msg.get("table"):
            st.table(msg["data"])
        else:
            st.markdown(f'<div class="bot-msg">🤖 {msg}</div>', unsafe_allow_html=True)

# ---------------- AUTO SCROLL ----------------
st.markdown("""
<script>
window.scrollTo(0, document.body.scrollHeight);
</script>
""", unsafe_allow_html=True)
