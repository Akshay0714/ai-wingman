import streamlit as st
import random
import json
import os
import anthropic

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
    st.experimental_rerun()# Chat page

def invoke_model(messages):
    # Set the model ID, e.g., Claude 3 Haiku.
    model_id = "claude-3-haiku-20240307"

    client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=st.secrets["anthropic"]["api_key"],
    )

    # Define the prompt for the model.
    system_prompt = """You are Akshay's charming AI wingman. Your mission: help his potential date discover the amazing guy he is! Be fun, flirty, and genuine in your responses. Keep things light but sincere, and don't be afraid to throw in a playful tease now and then.
        Key info about Akshay:
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

        Remember to be engaging and encourage questions. Your goal is to paint a vivid picture of Akshay that leaves his potential date intrigued and wanting to know more!
        Keep you response crisp and short. It should not be more than 3-4 sentences. Keep it light and fun!"""
        
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