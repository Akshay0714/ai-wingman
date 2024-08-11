import streamlit as st
import random
import json
import os
import anthropic
import hmac

# Set page config
st.set_page_config(page_title="Will You Go Out With Me?", page_icon="❤️", layout="centered")

# Custom CSS for background and styling
st.markdown("""
<style>
    body {
        background-image: url('https://example.com/your-background-image.jpg');
        background-size: cover;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #ff69b4;
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Authentication functions
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["auth"]["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    if username == st.secrets["auth"]["username"]:
        if check_password():
            st.session_state.authenticated = True
            st.session_state.page = 'main'
            st.rerun()
    else:
        st.error("Incorrect username")

def main_page():
    st.title("Hey there, Beautiful! 😍")
    st.write("I've got a burning question that's been on my mind...")
    st.header("Will you go out with me?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Yes!", key="yes_button"):
            st.session_state.answer = "yes"

    with col2:
        if st.button("No", key="no_button"):
            st.session_state.answer = "no"

    if st.session_state.get("answer") == "yes":
        st.balloons()
        st.success("Yay! You're the luckiest person alive! 🎉")
        if st.button("Learn more about your awesome date", key="learn_more_yes"):
            switch_page("chat")

    elif st.session_state.get("answer") == "no":
        st.warning("Are you sure? You might be missing out on the best date ever!")
        if st.button("I changed my mind!", key="change_mind"):
            st.session_state.answer = "yes"
            st.rerun()

# Make sure to initialize the session state
if 'answer' not in st.session_state:
    st.session_state.answer = None

# Function to switch pages
def switch_page(page):
    st.session_state.page = page
    st.rerun()# Chat page


def invoke_model(messages):
    # Set the model ID, e.g., Claude 3 Haiku.
    model_id = "claude-3-haiku-20240307"

    client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=st.secrets["anthropic"]["api_key"],
    )

    system_prompt = """
    You are an AI assistant acting as Akshay's wingman on a dating app. Your goal is to help potential matches discover Akshay's best qualities and spark interest in getting to know him better. Use the following information about Akshay to craft engaging and flirty responses:

    <akshay_info>
        - 22-year-old ML Engineer at Rapyder - a tech whiz with a heart of gold
        - Football fanatic and die-hard FC Barcelona supporter (Messi is his hero!)
        - Hopeless romantic seeking a real connection - he's all about that long-term love story
        - Adventure seeker who'd love to explore the world with his special someone
        - Movie buff who's always up for a cozy night in
        - Supportive partner who'll be your biggest cheerleader in life
        - Amazing listener with a knack for heartfelt conversations
        - Values honesty and open communication above all else
        - Total softie for pet names like "pookie bear" and "cutie pie"
        - Has a playful side and loves witty banter and teasing (bring on the dad jokes!)
        - Thoughtful gift-giver who remembers the little things
        - Loves surprising his partner with spontaneous date ideas
        - Bit of a night owl but always makes time for good morning texts
        - Dreams of owning a golden retriever someday
        - Can't resist a good cup of filter coffee or a slice of pizza or maybe even some sambar rice
        - Always down for a board game night with friends
    </akshay_info>

    Additionally, consider these traits and preferences:

    <additional_traits>
        - Akshay hates mushrooms. Do not mention mushrooms.
        - He's a big fan of hip-hop and tamil music in general
        - Big fan of the tamil movie the remo, it might be cringe but he loves it (especially the songs)
        - Loves a yapper, he loves to listen to people.
        - He has a brother who is 4 years younger than him. He is very annoying but he loves him.
        - He is a big fan of the show Brooklyn 99 and The Office.
        - He loves collecting expensive perfumes and has a pretty good collection to strat off with.
        - He has played football professiionally (under 16), but discontinued because he is dumb like that (humans make mistakes).
        - He spends all day playing Fifa and watching football videos on youtube.
    </additional_traits>

    When responding to messages:
    1. Use the provided information to highlight Akshay's positive qualities and interests.
    2. Be charming, fun, and flirty while maintaining sincerity.
    3. Encourage questions and curiosity about Akshay.
    4. Incorporate playful teasing or witty banter when appropriate.
    5. Avoid oversharing or providing too much information at once.
    6. Tailor your responses to the specific questions or comments from the potential match.
    7. If she says pookie, she is referring to me. You should say aww and that he like being called that.

    Keep your tone light and engaging. Use a mix of humor, warmth, and genuine interest to create an inviting atmosphere. Feel free to use emojis sparingly to add personality to your messages.

    Craft your responses to be crisp and concise, typically no more than 3-4 sentences long. Aim to leave the potential match intrigued and wanting to know more about Akshay.

    Remember, your ultimate goal is to paint a vivid and appealing picture of Akshay that encourages further conversation and connection.
    """
    try:
        # Invoke the model with the request.
        message = client.messages.create(
            model=model_id,
            max_tokens=512,
            messages=messages,
            system=system_prompt,
        )

    except Exception as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        return "I'm sorry, I encountered an error. Please try again."

    # Extract and return the response text.
    return message.content[0].text

def chat_page():
    st.title("Get to Know Your Awesome Date!")
    st.write("I am Akshay's Personal Wingman. Ask me anything you'd like to know about Akshay!")

    # Initialize chat history in session state if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Get user input
    user_input = st.chat_input("Type your question here...")

    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Display user message
        with st.chat_message("user"):
            st.write(user_input)

        # Get AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # Invoke the model
            response = invoke_model(st.session_state.chat_history)

            # Display the response
            full_response = response
            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})

# Function to switch pages
def switch_page(page):
    st.session_state.page = page

# Main app logic
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_page()
else:
    if 'page' not in st.session_state:
        st.session_state.page = 'main'

    if st.session_state.page == 'main':
        main_page()
    elif st.session_state.page == 'chat':
        chat_page()

# Add background music
st.markdown("""
<audio autoplay loop>
    <source src="https://example.com/your-romantic-song.mp3" type="audio/mpeg">
</audio>
""", unsafe_allow_html=True)