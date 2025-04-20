import streamlit as st
from groq import Groq
from PIL import Image
from dotenv import dotenv_values
from json import load, dump
import datetime
import os
import json

from ImageGeneration import generate_image_list  # Your own helper for image generation

# Load .env variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

# System prompt for the chatbot
SystemPrompt = f"""Hello, I am Ansh Raj But you have to call me Sir. You are a very accurate and advanced AI chatbot named Delta which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
"""

SystemChatBot = [{"role": "system", "content": SystemPrompt}]

# Helper to add real-time information
def RealTimeInformation():
    now = datetime.datetime.now()
    return f"""Please use this real time information if needed,
Day: {now.strftime("%A")}
Date: {now.strftime("%d")}
Month: {now.strftime("%B")}
Year: {now.strftime("%Y")}
Time: {now.strftime("%H")} hours:{now.strftime("%M")} minutes:{now.strftime("%S")} seconds"""

# Helper to clean the bot response
def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

# Chatbot function using Groq API
def ChatBot(Query):
    try:
        chat_log_path = r"Data/ChatLog.json"
        messages = []

        if os.path.exists(chat_log_path) and os.path.getsize(chat_log_path) > 0:
            with open(chat_log_path, "r") as f:
                try:
                    messages = load(f)
                except json.JSONDecodeError:
                    messages = []
                    with open(chat_log_path, "w") as wf:
                        dump(messages, wf)

        messages.append({"role": "user", "content": Query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealTimeInformation()}] + messages,
            max_tokens=1204,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        with open(chat_log_path, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request. Please try again later."

# ========== STREAMLIT APP ========== #

st.set_page_config(page_title="Delta AI", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { display: flex; flex-direction: column; height: 100vh; }
    #chat-container {
        display: flex; flex-direction: column; overflow-y: auto;
        max-height: 80vh; padding: 1rem; margin-bottom: 4rem;
    }
    .chat-message {
        padding: 0.75rem 1rem; margin: 0.5rem 0; border-radius: 10px;
        max-width: 80%; word-wrap: break-word; font-size: 16px;
    }
    .user { background-color: #d1f5d3; align-self: flex-end; color: #1a1a1a; }
    .bot { background-color: #f0f0f5; align-self: flex-start; color: #1a1a1a; }
    .input-container {
        position: fixed; bottom: 1rem; width: 100%; left: 0;
        background-color: white; padding: 0.75rem 1.5rem;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1); z-index: 100;
    }
    input[type="text"] {
        width: 90%; padding: 0.6rem; font-size: 16px;
        border-radius: 10px; border: 1px solid #ccc;
    }
    button {
        margin-left: 0.5rem; padding: 0.6rem 1rem; font-size: 16px;
        background-color: #4CAF50; color: white; border-radius: 10px;
        border: none; cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🧠 Delta AI Chat Assistant")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
st.markdown('<div id="chat-container">', unsafe_allow_html=True)

for role, message in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='chat-message user'><strong>You:</strong> {message}</div>", unsafe_allow_html=True)
    elif role == "bot":
        st.markdown(f"<div class='chat-message bot'><strong>Delta:</strong> {message}</div>", unsafe_allow_html=True)
    elif role == "bot_images":
        for image_path in message:
            image = Image.open(image_path)
            st.image(image, caption="Generated Image", use_column_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input section
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", placeholder="Ask something or say 'generate image of...'")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.chat_history.append(("user", user_input))

    if user_input.lower().startswith("generate image of"):
        prompt = user_input.replace("generate image of", "").strip()
        with st.spinner("🧠 Generating ultra-HD images..."):
            image_paths = generate_image_list(prompt)
        st.session_state.chat_history.append(("bot_images", image_paths))

    else:
        with st.spinner("🤖 Thinking..."):
            response = ChatBot(user_input)
        st.session_state.chat_history.append(("bot", response))
