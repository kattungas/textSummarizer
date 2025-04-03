import streamlit as st
import os
import requests
import tempfile
import wave
import json
import vosk  # Open-source speech recognition
from dotenv import load_dotenv

# Load API keys
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Streamlit UI setup
st.set_page_config(page_title="AI Meeting Notes Summarizer", layout="centered")
st.title("🎙️ AI-Powered Meeting Notes Summarizer (LLaMA + Vosk)")

# User input options
option = st.radio("Choose Input Method:", ("📄 Enter Text", "🎤 Upload Audio"))

user_input = ""

### 🔹 Speech-to-Text Using Vosk (Offline) ###
def transcribe_audio(audio_path):
    model = vosk.Model("model")  # Ensure Vosk model is downloaded and placed in a "model" directory
    wf = wave.open(audio_path, "rb")
    
    rec = vosk.KaldiRecognizer(model, wf.getframerate())
    transcript = ""

    while True:
        data = wf.readframes(4000)
        if not data:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            transcript += result.get("text", "") + " "

    wf.close()
    return transcript.strip()

if option == "📄 Enter Text":
    user_input = st.text_area("Enter meeting transcript or notes", height=300)

elif option == "🎤 Upload Audio":
    uploaded_file = st.file_uploader("Upload meeting recording (WAV format only)", type=["wav"])

    if uploaded_file:
        st.info("Processing audio transcription...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        # Transcribe using Vosk
        user_input = transcribe_audio(temp_file_path)

        st.success("Transcription complete! See below:")
        st.text_area("Transcribed Text:", value=user_input, height=200)

### 🔹 Summarization Using LLaMA via GROQ API ###
if st.button("Summarize") and user_input.strip():
    with st.spinner("Summarizing the meeting notes..."):
        try:
            prompt = f"""
            You are an expert editor. Summarize the following meeting notes clearly and concisely.
            Focus on key points discussed, decisions made, and action items.
            Avoid filler content, repetition, or opinions.
            Keep the summary under 10 words.

            Text to summarize:
            {user_input}
            """

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-70b-8192",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 300
                }
            )
            data = response.json()
            summary = data["choices"][0]["message"]["content"]

            st.subheader("📌 Summary:")
            st.success(summary)

        except Exception as e:
            st.error(f"Error: {e}")