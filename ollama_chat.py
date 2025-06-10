import streamlit as st
import requests
import json
import os
from datetime import datetime
from docx import Document
import fitz  # for PDF reading
import speech_recognition as sr

st.set_page_config(page_title="Ollama Chat+", page_icon="🧠", layout="wide")
st.title("Ollama Chat+ (w/ Voice, Files, Tabs)")

# Load custom CSS if it exists
def load_css(path):
    try:
        with open(path) as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found.")

load_css("styles/main.css")

# Set up state defaults
state = st.session_state
state.setdefault("tabs", {"Chat 1": []})
state.setdefault("current_tab", "Chat 1")
state.setdefault("assistant_name", "LLaMA 3")
state.setdefault("temperature", 0.7)
state.setdefault("maxtokens", 400)

# Sidebar config
with st.sidebar:
    st.header("Settings")

    new_name = st.text_input("Assistant Name", state.assistant_name)
    state.assistant_name = new_name.strip() if new_name.strip() else state.assistant_name

    state.temperature = st.slider("Temperature", 0.0, 1.0, state.temperature, 0.05)
    state.maxtokens = st.slider("Max Tokens", 100, 1000, state.maxtokens, 50)

    new_tab = st.text_input("New Chat Tab")
    if st.button("Create New Tab") and new_tab.strip():
        state.tabs[new_tab.strip()] = []
        state.current_tab = new_tab.strip()

    selected_tab = st.selectbox("Choose Tab", list(state.tabs.keys()))
    state.current_tab = selected_tab

    if st.button("Clear This Tab"):
        state.tabs[selected_tab] = [{"role": "assistant", "content": f"Hey! I'm {state.assistant_name}, ready to help."}]

# Core functions
def call_local_llm(prompt):
    try:
        resp = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3",
            "prompt": prompt,
            "temperature": state.temperature,
            "stream": False
        })
        return resp.json().get("response", "") if resp.status_code == 200 else "Error from API"
    except Exception as e:
        return f"Request failed: {e}"

def save_chat():
    os.makedirs("chat_logs", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    chat_data = state.tabs[state.current_tab]
    filename = f"{state.current_tab}_{ts}.json"
    with open(os.path.join("chat_logs", filename), "w") as f:
        json.dump(chat_data, f, indent=2)

def read_uploaded_file(file):
    name = file.name
    if name.endswith(".txt"):
        return file.read().decode("utf-8")
    elif name.endswith(".docx"):
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    elif name.endswith(".pdf"):
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join(page.get_text() for page in pdf)
    return "Unsupported file format."

def transcribe_audio_file(file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Couldn’t understand the audio."

# Display chat history
chat = state.tabs[state.current_tab]
if not chat:
    chat.append({"role": "assistant", "content": f"Hey there, I'm {state.assistant_name}. What's up?"})

for msg in chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# Input + File/Voice interactions
user_input = st.chat_input("Say something...")

with st.expander("🎤 Upload Audio"):
    audio_file = st.file_uploader("WAV format only", type=["wav"])
    if st.button("Transcribe and Use") and audio_file:
        user_input = transcribe_audio_file(audio_file)
        st.success(f"Transcribed: {user_input}")

with st.expander("📁 Upload File for Summary"):
    file = st.file_uploader("Accepted: .txt, .pdf, .docx", type=["txt", "pdf", "docx"])
    if st.button("Summarize File") and file:
        content = read_uploaded_file(file)
        user_input = f"Summarize this content:\n\n{content[:3000]}"

# Process user input
if user_input:
    st.chat_message("user").markdown(user_input)
    chat.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner(f"{state.assistant_name} is replying..."):
            bot_reply = call_local_llm(user_input)
            st.markdown(bot_reply, unsafe_allow_html=True)

    chat.append({"role": "assistant", "content": bot_reply})
    save_chat()
