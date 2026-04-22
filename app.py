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

st.title("🗳 Election Assistant GPT")
st.caption("🇮🇳 Smart AI for Indian Elections & Politics")

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

# ---------------- SMART ELECTION RESPONSES ----------------
def smart_response(q):
    q = q.lower()

    if "document" in q or "id" in q:
        return "📄 Documents: Aadhaar, Voter ID, Passport, Address Proof"

    if "voting process" in q or "how to vote" in q:
        return """🗳 Voting Process:
1. Check voter list
2. Visit polling booth
3. Verify identity
4. Cast vote using EVM"""

    if "eligibility" in q:
        return "🧾 Must be 18+ and registered voter"

    if "register" in q:
        return "📝 Register at https://www.nvsp.in using Form 6"

    return None

# ---------------- VOTER ID PROCESS ----------------
def voter_id_process(q):
    q = q.lower()

    if "voter id process" in q or "apply voter id" in q:
        return """📝 Voter ID Registration:

1️⃣ Visit https://www.nvsp.in  
2️⃣ Select 'New Registration' (Form 6)  
3️⃣ Fill details  
4️⃣ Upload documents  
5️⃣ Submit  
6️⃣ Track status  

📌 Ensure correct details."""

    return None

# ---------------- CM DETECTION ----------------
def get_cm_info(q):
    q = q.lower()

    cm_data = {
        "tamil nadu": "M.K. Stalin",
        "kerala": "Pinarayi Vijayan",
        "karnataka": "Siddaramaiah",
        "andhra pradesh": "N. Chandrababu Naidu",
        "telangana": "Revanth Reddy",
        "maharashtra": "Eknath Shinde",
        "uttar pradesh": "Yogi Adityanath"
    }

    for state in cm_data:
        if state in q:
            return f"🏛 Chief Minister of {state.title()}: {cm_data[state]}"

    return None

# ---------------- POLITICAL KNOWLEDGE ----------------
def political_knowledge(q):
    q = q.lower()

    if "prime minister" in q or "pm of india" in q:
        return "🇮🇳 Prime Minister of India: Narendra Modi"

    if "president of india" in q:
        return "🇮🇳 President of India: Droupadi Murmu"

    if "nda" in q:
        return "🟠 NDA (National Democratic Alliance): BJP-led ruling alliance."

    if "india alliance" in q:
        return "🔵 INDIA Alliance: Coalition of opposition parties."

    if "constitution" in q:
        return "📜 The Indian Constitution is the supreme law of India, adopted in 1950."

    if "election commission" in q:
        return "🏛 Election Commission of India conducts elections and ensures fairness."

    return None

# ---------------- PARTY COMPARISON ----------------
def party_comparison(q):
    q = q.lower()

    if "nda vs india" in q or "party comparison" in q:
        return {
            "table": True,
            "data": [
                ["Alliance", "Leader", "Type"],
                ["NDA", "BJP-led", "Ruling Alliance"],
                ["INDIA", "Opposition Coalition", "Opposition"]
            ]
        }

    return None

# ---------------- WEB SEARCH ----------------
def web_search_answer(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return f"🌐 From Web:\n{summary}"
    except:
        return None

# ---------------- AI RESPONSE ----------------
def get_ai_response(user_input):

    # Rule-based
    for func in [smart_response, voter_id_process, get_cm_info, political_knowledge, party_comparison]:
        result = func(user_input)
        if result:
            return result

    # Gemini AI (Enhanced prompt)
    try:
        prompt = f"""
        You are an expert Election and Indian Politics Assistant.

        Provide:
        - Clear explanation
        - Relevant Indian political context
        - Avoid repetition

        Question: {user_input}
        """
        res = model.generate_content(prompt)

        if res and res.text:
            return res.text
    except:
        pass

    # Web fallback
    web = web_search_answer(user_input)
    if web:
        return web

    return "⚠️ Please ask election or Indian political related questions."

# ---------------- SUGGESTIONS ----------------
st.subheader("💡 Suggested Questions")

suggestions = [
    "Who is PM of India?",
    "CM of Tamil Nadu?",
    "Explain Indian Constitution",
    "NDA vs INDIA",
    "How to apply voter ID?"
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

# ---------------- DISPLAY ----------------
for role, msg in st.session_state.chat:
    if role == "user":
        st.success("👤 " + msg)
    else:
        if isinstance(msg, dict) and msg.get("table"):
            st.table(msg["data"])
        else:
            st.info("🤖 " + msg)
