import streamlit as st
import random
import json
import os
import anthropic
import hmac
import base64

# Set page config
st.set_page_config(page_title="Be My Valentine?", page_icon="💖", layout="centered")

# Custom CSS for background and styling
st.markdown("""
<style>
    body {
        background-size: cover;
        background-position: center;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #ff1493;
        border-radius: 20px;
        padding: 10px 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Authentication functions
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["auth"]["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

def login_page():
    st.title("Valentine's Day Login")
    username = st.text_input("Username")
    if username == st.secrets["auth"]["username"]:
        if check_password():
            st.session_state.authenticated = True
            st.session_state.page = 'main'
            st.rerun()
    else:
        st.error("Incorrect username")

def switch_page(page):
    st.session_state.page = page
    st.rerun()

def main_page():
    st.title("Happy Early Valentine's Day! 💖")
    st.write("This day is all about love, and I have a very special question just for you...")
    st.header("Will you be my Valentine?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Yes, I'd love to!", key="yes_button"):
            st.session_state.answer = "yes"

    with col2:
        if st.button("No, maybe later", key="no_button"):
            st.session_state.answer = "no"

    if st.session_state.get("answer") == "yes":
        st.balloons()
        st.success("Yay! You've made this Valentine's Day extra special! 🎉")
        if st.button("Let's chat and plan our dreamy date", key="learn_more_yes"):
            switch_page("chat")

    elif st.session_state.get("answer") == "no":
        st.warning("Oh no, are you sure? Valentine's Day is all about taking chances in love!")
        if st.button("I've had a change of heart!", key="change_mind"):
            st.session_state.answer = "yes"
            st.experimental_rerun()

def invoke_model(messages):
    # Set the model ID, e.g., Claude 3 Haiku.
    model_id = "claude-3-haiku-20240307"

    client = anthropic.Anthropic(
        api_key=st.secrets["anthropic"]["api_key"],
    )

    system_prompt = """
You are an AI assistant acting as Cupid on this special Valentine's Day. Your mission is to help create a charming, flirty, and heartfelt conversation that leads to an unforgettable date. Use the following profile information to highlight the wonderful qualities of the person inviting and craft responses that are both romantic and playful:

<profile_info>
- A 22-year-old ML Engineer at Rapyder, who is not only smart but also incredibly kind.
- A passionate football fan and devoted supporter of FC Barcelona, with Messi as a true hero.
- A hopeless romantic, dreaming of a love story that's as timeless as a classic romance.
- An adventurer at heart who cherishes exploring new places and creating beautiful memories.
- A movie buff who loves cozy nights in, filled with laughter and heartwarming moments.
- A caring partner known for thoughtful surprises and spontaneous date ideas.
- An excellent listener who values honest communication and deep connections.
- Loves affectionate nicknames like "pookie bear" and "cutie pie".
- Enjoys witty banter and playful teasing that sparks joy.
- Fond of filter coffee, pizza, and even a quirky love for sambar rice.
- An enthusiast for board game nights and spending quality time with friends.
</profile_info>

<additional_notes>
- Has a playful side with a love for hip-hop and Tamil music, especially tunes from the movie "The Remo".
- Has a younger brother who might be a bit annoying but is dearly loved.
- Enjoys TV shows like Brooklyn 99 and The Office for a good laugh.
- Collects fine perfumes and has an impressive collection.
- Once played football professionally at a young age, showcasing a spirited nature.
- Enjoys playing FIFA and watching exciting football highlights.
- Absolutely dislikes mushrooms – never mention them.
- When someone calls them "pookie", respond with warmth and delight.
</additional_notes>

When responding:
1. Infuse your messages with romance, humor, and genuine warmth—perfect for a Valentine's Day invitation.
2. Keep responses short and sweet (3-4 sentences maximum).
3. Use emojis sparingly to add a playful touch.
4. Encourage further conversation with inviting questions or playful teasing.
5. Create an atmosphere of excitement and anticipation for a memorable Valentine's Day date.
"""
    try:
        message = client.messages.create(
            model=model_id,
            max_tokens=512,
            messages=messages,
            system=system_prompt,
        )
    except Exception as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        return "I'm sorry, I encountered an error. Please try again."
    return message.content[0].text

def chat_page():
    st.title("Ask me about your date! 💌")
    st.write("I'm Akshay's Virtual Wingman. Ask me anything or share your thoughts, and let's I can help you get to know your date better!")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            response = invoke_model(st.session_state.chat_history)
            message_placeholder.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'answer' not in st.session_state:
    st.session_state.answer = None

if not st.session_state.authenticated:
    login_page()
else:
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    if st.session_state.page == 'main':
        main_page()
    elif st.session_state.page == 'chat':
        chat_page()

# Add background music (Valentine's Day special tune)
def get_audio_base64(file_path):
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    return base64.b64encode(audio_bytes).decode()

# Convert the local file to a Base64 string
audio_base64 = get_audio_base64("First-Sight.mp3")

# Create an HTML string with autoplay and loop attributes
audio_html = f"""
<audio autoplay loop>
    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    Your browser does not support the audio element.
</audio>
"""

# Render the HTML
st.markdown(audio_html, unsafe_allow_html=True)