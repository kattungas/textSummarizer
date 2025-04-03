import streamlit as st
import os
import requests
from dotenv import load_dotenv
import base64
 
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
logo_path = "MOURI_Tech_Logo.png"  # Ensure this file exists in the same directory
# Set page configuration with favicon

st.set_page_config(page_title="MOURI Tech - Summarizer", layout="centered")
# Add a logo

#st.image(logo_path, width=150)  # Adjust width as needed
logo_html = f"""
    <div style="position: absolute; top: 10px; left: 10px;">
        <img src="data:image/png;base64,{base64.b64encode(open(logo_path, "rb").read()).decode()}" width="200" height="50">
    </div>
    <div style="height: 50px;"></div>  <!-- Adds space after the logo -->
"""
st.markdown(logo_html, unsafe_allow_html=True)
st.title("Meeting Notes Summarizer")
 
user_input = st.text_area(
    "Convert Meeting Conversations into Summarized Insights", height=300)
 
 
prompt = f"""
You are a professional meeting summarizer. Provide a structured summary of the meeting notes.
Follow this format:
1. **Key Discussion Points**:
   - (List main topics discussed)
2. **Decisions Made**:
   - (List key decisions)
3. **Action Items**:
   - (List tasks with responsible persons)

Meeting Notes:
{user_input}
"""
 
summary = ""  # Ensure summary is defined before usage
if st.button("Summarize"):
    if not user_input.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Summarizing the meeting transcripts..."):
            try:
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
                if "choices" in data:
                    summary = data["choices"][0]["message"]["content"]
                    st.subheader("Summary:")
                    st.success(summary)
                else:
                    st.error("Unexpected response format. Please try again.")
            except requests.exceptions.RequestException as e:
                st.error(f"API Error: {e}")
            except KeyError:
                st.error("Error processing response from API.")

def get_text_download_link(text, filename="summary.txt"):
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 Download Summary</a>'

if summary:
    st.markdown(get_text_download_link(summary), unsafe_allow_html=True)