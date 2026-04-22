import streamlit as st
import speech_recognition as sr
from googletrans import Translator
import matplotlib.pyplot as plt
import google.generativeai as genai

# 🔑 Gemini API Key
genai.configure(api_key="AIzaSyBTAZG3YTiLzOaz-qT2OHbSwOXIUf5rHqU")

model = genai.GenerativeModel("gemini-pro")

# Page config
st.set_page_config(page_title="Election Assistant", layout="wide")

# Custom CSS (Professional UI)
st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
.chat-box {
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.user {
    background-color: #d1e7dd;
}
.bot {
    background-color: #f8d7da;
}
</style>
""", unsafe_allow_html=True)

# Title
st.title("🗳 AI Election Assistant")
st.caption("Smart assistant for election education")

# Sidebar
st.sidebar.title("⚙️ Settings")

# Language selection
translator = Translator()
language = st.sidebar.selectbox("🌐 Language", ["English", "Tamil", "Hindi"])

def translate_text(text):
    if language == "Tamil":
        return translator.translate(text, dest='ta').text
    elif language == "Hindi":
        return translator.translate(text, dest='hi').text
    return text

# Chat history
if "chat" not in st.session_state:
    st.session_state.chat = []

# Layout
col1, col2 = st.columns([2, 1])

# LEFT SIDE (Chat)
with col1:
    st.subheader("💬 Chat with Assistant")

    user_input = st.text_input("Type your question:")

    if user_input:
        try:
            response = model.generate_content(user_input).text
        except:
            response = "AI service error. Try again."

        translated = translate_text(response)

        st.session_state.chat.append(("user", user_input))
        st.session_state.chat.append(("bot", translated))

    # Display chat
    for role, msg in st.session_state.chat:
        if role == "user":
            st.markdown(f'<div class="chat-box user">👤 {msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-box bot">🤖 {msg}</div>', unsafe_allow_html=True)

# RIGHT SIDE (Features)
with col2:
    st.subheader("🎤 Voice Input")

    if st.button("Speak"):
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                st.info("Listening...")
                audio = r.listen(source)

            text = r.recognize_google(audio)
            st.success(f"You said: {text}")

            response = model.generate_content(text).text
            st.write(translate_text(response))

        except:
            st.error("Voice recognition failed")

    st.subheader("📊 Timeline")

    if st.button("Show Timeline"):
        steps = ["Announcement", "Campaign", "Voting", "Counting", "Results"]
        values = [1, 2, 3, 4, 5]

        plt.figure()
        plt.plot(steps, values)
        plt.title("Election Timeline")

        st.pyplot(plt)

    st.subheader("📍 Location")

    st.markdown("[Find Polling Stations](https://www.google.com/maps)")
