import streamlit as st
import google.generativeai as genai
import pandas as pd
import wikipedia
import time
import os

# ---------------- CONFIG ----------------
genai.configure(api_key="AIzaSyDNDy21ZlSFAPkjRvRdgPfPb1bsjwxafBE")
model = genai.GenerativeModel("gemini-pro")

st.set_page_config(page_title="Indian Election AI Assistant", layout="wide")

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
st.caption("AI + Data + Insights Platform")

# ---------------- LOAD DATA (FIXED) ----------------
@st.cache_data
def load_data():
    file_path = "Indian General Elections 2024.csv"

    if not os.path.exists(file_path):
        return None

    try:
        return pd.read_csv(file_path, encoding="utf-8")
    except:
        try:
            return pd.read_csv(file_path, encoding="latin1")
        except:
            try:
                return pd.read_csv(file_path, encoding="ISO-8859-1")
            except Exception as e:
                st.error(f"❌ Dataset Error: {e}")
                return None

df = load_data()

# Upload fallback
uploaded_file = st.sidebar.file_uploader("📂 Upload CSV", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("✅ Dataset loaded!")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# ---------------- DEBUG ----------------
if df is not None:
    st.success("✅ Dataset Loaded Successfully")

# ---------------- SESSION ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.chat = []

# ---------------- CHATBOT ----------------
def gemini_answer(query):
    try:
        prompt = f"""
        You are a helpful AI assistant.

        - Answer like ChatGPT
        - If election-related → focus on Indian elections
        - Be clear and structured

        Question: {query}
        """
        res = model.generate_content(prompt)
        if res and res.text:
            return res.text
    except:
        return None

def wiki_answer(query):
    try:
        return wikipedia.summary(query + " India", sentences=3)
    except:
        return None

def handle_greeting(q):
    if q.lower().strip() in ["hi", "hello", "hey"]:
        return "👋 Hello! Ask me anything about elections, data insights, or general topics."
    return None

def generate_response(user_input):

    greet = handle_greeting(user_input)
    if greet:
        return greet

    ai = gemini_answer(user_input)
    if ai:
        return ai

    wiki = wiki_answer(user_input)
    if wiki:
        return "🌐 " + wiki

    return "🤖 I'm here to help! Please rephrase your question."

# ---------------- INPUT ----------------
user_input = st.text_input("💬 Ask your question:")

if user_input:
    st.session_state.chat.append(("user", user_input))

    placeholder = st.empty()
    placeholder.markdown("🤖 Thinking...")
    time.sleep(1)

    response = generate_response(user_input)

    placeholder.empty()
    st.session_state.chat.append(("bot", response))

# ---------------- DISPLAY CHAT ----------------
st.subheader("💬 Conversation")

for role, msg in st.session_state.chat[-10:]:
    if role == "user":
        st.markdown(f'<div class="user-msg">👤 {msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">🤖 {msg}</div>', unsafe_allow_html=True)

# ---------------- ANALYTICS ----------------
st.subheader("📊 Election Analytics")

if df is not None:

    # -------- PARTY-WISE --------
    party_col = next((c for c in df.columns if "party" in c.lower()), None)

    if party_col:
        st.markdown("### 🏛 Party-wise Seats")
        party_counts = df[party_col].value_counts()
        st.bar_chart(party_counts)

    # -------- STATE-WISE --------
    state_col = next((c for c in df.columns if "state" in c.lower()), None)

    if state_col:
        st.markdown("### 🗺 State-wise Analysis")

        selected_state = st.selectbox("Select State", df[state_col].dropna().unique())

        state_data = df[df[state_col] == selected_state]

        st.write(f"📍 Total Seats: {len(state_data)}")

        if party_col:
            st.bar_chart(state_data[party_col].value_counts())

    else:
        st.warning("⚠️ No State column found")

    # -------- AI INSIGHTS --------
    st.markdown("### 🧠 AI Insights")

    if st.button("Generate Insights"):
        with st.spinner("Analyzing election data..."):
            try:
                sample = df.head(20).to_string()

                prompt = f"""
                Analyze this Indian election dataset.

                Provide:
                - Dominant party
                - Trends
                - Summary

                Data:
                {sample}
                """

                res = model.generate_content(prompt)

                if res and res.text:
                    st.success(res.text)
                else:
                    st.warning("No insights generated")

            except Exception as e:
                st.error(f"Error: {e}")

else:
    st.info("📂 Upload or place CSV file to enable analytics")

# ---------------- AUTO SCROLL ----------------
st.markdown("""
<script>
window.scrollTo(0, document.body.scrollHeight);
</script>
""", unsafe_allow_html=True)
