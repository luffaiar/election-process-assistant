import streamlit as st
from logic import get_response
import speech_recognition as sr
from googletrans import Translator
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Election Assistant")

st.title("🗳 Election Process Assistant")
st.write("Learn election process interactively!")

# Language selection
translator = Translator()
language = st.selectbox("🌐 Select Language", ["English", "Tamil", "Hindi"])

def translate_text(text):
    if language == "Tamil":
        return translator.translate(text, dest='ta').text
    elif language == "Hindi":
        return translator.translate(text, dest='hi').text
    return text

# Text input
user_input = st.text_input("Ask your question:")

if user_input:
    response = get_response(user_input)
    translated = translate_text(response)
    st.success(translated)

# Voice input
st.subheader("🎤 Voice Input")

if st.button("Speak"):
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("Listening...")
            audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio)
        st.success(f"You said: {text}")

        response = get_response(text)
        translated = translate_text(response)
        st.write(translated)

    except:
        st.error("❌ Could not understand audio")

# Timeline Visualization
st.subheader("📊 Election Timeline")

if st.button("Show Timeline"):
    steps = ["Announcement", "Campaign", "Voting", "Counting", "Results"]
    values = [1, 2, 3, 4, 5]

    plt.figure()
    plt.plot(steps, values)
    plt.title("Election Process Timeline")
    plt.xlabel("Stages")
    plt.ylabel("Order")

    st.pyplot(plt)

# Google Maps Link
st.markdown("📍 Find polling stations: https://www.google.com/maps")
