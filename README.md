# Ollama Chat+ (Streamlit App)

This is a simple and flexible chat interface built with Streamlit, designed to work with a local LLaMA 3 model (served via Ollama). It includes extra features like:

- Multiple chat tabs
- Voice message input via `.wav` files
- File upload for summarising `.txt`, `.pdf`, and `.docx` documents

---

## Features

- **Chat tabs**: Keep your conversations organised by topic.
- **Voice transcription**: Upload audio and turn it into text using Google's speech recognition.
- **File reading**: Quickly extract and summarise content from documents.
- **Custom assistant**: Rename your assistant and tweak its behavior (temperature, token limit).

---

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start your local Ollama model 
```bash
ollama serve
```
Make sure LLaMA 3 is pulled and ready to use:

```bash
ollama run llama3
```

### 3. Run the app

```bash
streamlit run app.py
```