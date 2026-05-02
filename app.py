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

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    if os.path.exists("Indian General Elections 2024.csv"):
        return pd.read_csv("Indian General Elections 2024.csv")
    return None

df = load_data()

uploaded_file = st.sidebar.file_uploader("📂 Upload CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Dataset loaded!")

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

        Answer naturally like ChatGPT.
        If election-related, focus on Indian election system.

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

def generate_response(user_input):
    ai = gemini_answer(user_input)
    if ai:
        return ai

    wiki = wiki_answer(user_input)
    if wiki:
        return "🌐 " + wiki

    return "🤖 Please rephrase your question."

# ---------------- CHAT INPUT ----------------
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
    if "Party" in df.columns:
        st.markdown("### 🏛 Party-wise Seats")
        party_counts = df["Party"].value_counts()
        st.bar_chart(party_counts)

    # -------- STATE-WISE --------
    state_column = None
    for col in df.columns:
        if "state" in col.lower():
            state_column = col
            break

    if state_column:
        st.markdown("### 🗺 State-wise Analysis")

        selected_state = st.selectbox("Select State", df[state_column].dropna().unique())

        state_data = df[df[state_column] == selected_state]

        st.write(f"📍 Total Seats in {selected_state}: {len(state_data)}")

        if "Party" in df.columns:
            state_party = state_data["Party"].value_counts()
            st.bar_chart(state_party)

    else:
        st.warning("⚠️ No 'State' column found in dataset")

    # -------- AI INSIGHTS --------
    st.markdown("### 🧠 AI Insights")

    if st.button("Generate Insights"):
        with st.spinner("Analyzing data..."):

            sample = df.head(20).to_string()

            prompt = f"""
            Analyze this Indian election dataset and provide insights:

            - Dominant party
            - State trends
            - Overall conclusion

            Data:
            {sample}
            """

            res = model.generate_content(prompt)

            if res and res.text:
                st.success(res.text)
            else:
                st.warning("Could not generate insights")

else:
    st.info("📂 Upload or place CSV file to enable analytics")

# ---------------- AUTO SCROLL ----------------
st.markdown("""
<script>
window.scrollTo(0, document.body.scrollHeight);
</script>
""", unsafe_allow_html=True)
