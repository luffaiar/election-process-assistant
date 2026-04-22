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
st.caption("🇮🇳 Detailed Guidance for Elections & Political Awareness")

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

# ---------------- DETAILED KNOWLEDGE ----------------
def detailed_guidance(q):
    q = q.lower()

    if "voter id" in q or "register" in q:
        return """📝 **Voter ID Registration Process (India)**

1. Visit the official portal: https://www.nvsp.in  
2. Click on “New Voter Registration (Form 6)”  
3. Enter personal details (Name, DOB, Address)  
4. Upload required documents:
   - Identity proof (Aadhaar, Passport)
   - Address proof  
5. Submit the application  
6. Track status using your reference ID  

📌 Ensure all details are accurate to avoid rejection."""

    if "voting process" in q or "how to vote" in q:
        return """🗳 **Voting Process in India**

1. Check your name in the voter list  
2. Visit your assigned polling booth  
3. Show valid ID for verification  
4. Receive slip and proceed to voting machine  
5. Cast your vote using EVM  
6. Verify VVPAT slip  

📌 Follow instructions from polling officers."""

    if "eligibility" in q:
        return """🧾 **Eligibility to Vote**

- Must be an Indian citizen  
- Must be 18 years or older  
- Must be registered in the voter list  
- Must have valid identification  

📌 Register early to avoid last-minute issues."""

    return None

# ---------------- POLITICAL KNOWLEDGE ----------------
def political_knowledge(q):
    q = q.lower()

    if "prime minister" in q:
        return """🇮🇳 **Prime Minister of India**

Narendra Modi is the current Prime Minister of India.  
The Prime Minister is the head of the government and is responsible for decision-making and policy implementation."""

    if "constitution" in q:
        return """📜 **Indian Constitution**

The Constitution of India is the supreme law of the country.  
It defines the structure of government, rights of citizens, and duties of institutions.  
It came into effect on January 26, 1950."""

    return None

# ---------------- WEB SEARCH ----------------
def web_search(query):
    try:
        return wikipedia.summary(query, sentences=3)
    except:
        return None

# ---------------- AI RESPONSE ----------------
def get_ai_response(user_input):

    # Step 1: Detailed guidance
    detail = detailed_guidance(user_input)
    if detail:
        return detail

    # Step 2: Political knowledge
    political = political_knowledge(user_input)
    if political:
        return political

    # Step 3: AI (structured response)
    try:
        prompt = f"""
        You are an official Election Assistant.

        Provide:
        - Detailed explanation
        - Step-by-step guidance if applicable
        - Clear and structured answer

        Question: {user_input}
        """
        res = model.generate_content(prompt)

        if res and res.text:
            return res.text
    except:
        pass

    # Step 4: Web fallback
    web = web_search(user_input)
    if web:
        return "🌐 " + web

    return "⚠️ Please ask election-related questions."

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

# ---------------- LIMIT HISTORY ----------------
if len(st.session_state.chat) > 8:
    st.session_state.chat = st.session_state.chat[-8:]

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
