import streamlit as st
from chatbot import ChatBot
from ImageGeneration import generate_image_list  # Your helper
from PIL import Image
import os

# Streamlit page configuration
st.set_page_config(page_title="Delta AI", layout="wide")

# Apply custom CSS for styling
st.markdown("""
    <style>
    .main {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    #chat-container {
        display: flex;
        flex-direction: column;
        overflow-y: auto;
        max-height: 80vh;
        padding: 1rem;
        margin-bottom: 4rem;  /* Adjust space for the input box */
    }
    .chat-message {
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        max-width: 80%;
        word-wrap: break-word;
        font-size: 16px;
    }
    .user {
        background-color: #d1f5d3;
        align-self: flex-end;
        color: #1a1a1a;
    }
    .bot {
        background-color: #f0f0f5;
        align-self: flex-start;
        color: #1a1a1a;
    }
    .input-container {
        position: fixed;
        bottom: 1rem;
        width: 100%;
        left: 0;
        background-color: white;
        padding: 0.75rem 1.5rem;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        z-index: 100;
    }
    input[type="text"] {
        width: 90%;
        padding: 0.6rem;
        font-size: 16px;
        border-radius: 10px;
        border: 1px solid #ccc;
    }
    button {
        margin-left: 0.5rem;
        padding: 0.6rem 1rem;
        font-size: 16px;
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        border: none;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🧠 Delta AI Chat Assistant")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat display
st.markdown('<div id="chat-container">', unsafe_allow_html=True)

# Display chat history (User and Bot messages)
for role, message in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='chat-message user'><strong>You:</strong> {message}</div>", unsafe_allow_html=True)
    elif role == "bot":
        st.markdown(f"<div class='chat-message bot'><strong>Delta:</strong> {message}</div>", unsafe_allow_html=True)
    elif role == "bot_images":
        # Display images for bot responses
        for image_path in message:
            image = Image.open(image_path)
            st.image(image, caption=f"Generated Image", use_column_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input box for new messages
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", placeholder="Ask something or give something to Summarize")  # No extra input box
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    # Add user message to chat history
    st.session_state.chat_history.append(("user", user_input))

    # Check if it's an image generation request
    if user_input.lower().startswith("generate image of"):
        prompt = user_input.replace("generate image of", "").strip()

        with st.spinner("🧠 Generating ultra-HD images..."):
            image_paths = generate_image_list(prompt)

        # Add image paths to chat history (Bot message with images)
        st.session_state.chat_history.append(("bot_images", image_paths))

    else:
        # Chatbot text response
        response = ChatBot(user_input)
        st.session_state.chat_history.append(("bot", response))

# Since Streamlit auto-updates the page when data in session_state is changed,
# there's no need to explicitly rerun the app.
