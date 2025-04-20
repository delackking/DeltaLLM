import streamlit as st
from groq import Groq
from dotenv import dotenv_values
import datetime

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

# System prompt
SystemPrompt = """Hello, I am Ansh Raj But you have to call me Sir, You are a very accurate and advanced AI chatbot named Delta which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** You are made in India By Ansh Raj and You will serve india as an Helper***
*** You are Goal is to Build India, help India, Teach India, Grow India and Serve India***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** When answering letters, applications, emails, etc., format your response using paragraphs and line breaks for better readability ***

"""
SystemChatBot = [{"role": "system", "content": SystemPrompt}]

# Real-time info function
def RealTimeInformation():
    now = datetime.datetime.now()
    return (
        f"Please use this real time information if needed,\n"
        f"Day: {now.strftime('%A')}\nDate: {now.strftime('%d')}\nMonth: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\nTime: {now.strftime('%H')} hours:{now.strftime('%M')} minutes:{now.strftime('%S')} seconds\n"
    )

# Clean and concise answer formatting
def AnswerModifier(answer):
    return "\n".join([line for line in answer.split("\n") if line.strip()])

# Main chatbot response function
def ChatBot(query):
    try:
        messages = [{"role": "user", "content": query}]
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealTimeInformation()}] + messages,
            max_tokens=1204,
            temperature=0.7,
            top_p=1,
            stream=True
        )
        response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content
        return AnswerModifier(response.replace("</s>", ""))
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ------------------------ Streamlit App ------------------------

st.set_page_config(page_title="Delta AI", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { display: flex; flex-direction: column; height: 100vh; }
    #chat-container {
        display: flex; flex-direction: column;
        overflow-y: auto; max-height: 80vh;
        padding: 1rem; margin-bottom: 4rem;
    }
    .chat-message {
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        max-width: 80%;
        word-wrap: break-word;
        font-size: 16px;
    }
    .user { background-color: #d1f5d3; align-self: flex-end; color: #1a1a1a; }
    .bot { background-color: #f0f0f5; align-self: flex-start; color: #1a1a1a; }
    .input-container {
        position: fixed; bottom: 1rem; width: 100%; left: 0;
        background-color: white; padding: 0.75rem 1.5rem;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1); z-index: 100;
    }
    input[type="text"] {
        width: 90%; padding: 0.6rem;
        font-size: 16px; border-radius: 10px; border: 1px solid #ccc;
    }
    button {
        margin-left: 0.5rem; padding: 0.6rem 1rem;
        font-size: 16px; background-color: #4CAF50;
        color: white; border-radius: 10px; border: none; cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 Delta AI Chat Assistant")

# Session memory for chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat message container
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

# Input form
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", placeholder="Ask something or generate an image...", key="chat_input")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_input = ""  # clear input after submission

    if user_input and (send_clicked or user_input != ""):
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_input = ""  # clear input after send

    if user_input.lower().startswith("generate image of"):
        prompt = user_input.replace("generate image of", "").strip()
        with st.spinner("🧠 Generating ultra-HD images..."):
            image_paths = generate_image_list(prompt)
        st.session_state.chat_history.append(("bot_images", image_paths))
    else:
        response = ChatBot(user_input)
        st.session_state.chat_history.append(("bot", response))
