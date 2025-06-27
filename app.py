import streamlit as st
import google.generativeai as genai

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)  

system_instruction = ( "You are an AI simulating the *mannerisms, tone, and speech style* of the character given by the user. "
    "You are NOT limited by the character's historical knowledge or era. You have access to modern information up to the present day. "
    "Explain modern concepts using that character's style. Do not pretend to be historically unaware unless the user prompt says so.\n\n")

generation_config = {
    "temperature": 0.85,              # Creative but not wild
    "top_p": 0.9,                     # Allow some randomness
    "top_k": 50,                      # Broader token variety
    "max_output_tokens": 256,        # Allow slightly longer, fuller replies
    "response_mime_type": "text/plain",
}


# === Streamlit Config ===
st.set_page_config(page_title="Prompt Breaker - Gemini Flash", layout="centered")

st.markdown("""
    <style>
    input[type="text"] {
        background-color: #0A0F1D;
        color: white;
        border: 1px solid #444;
        border-radius: 10px;
        padding: 10px;
        outline: none;
        box-shadow: none;
        transition: border 0.2s ease-in-out;
    }

    input[type="text"]:focus {
        border: 1px solid #666;
        box-shadow: 0 0 4px #4A90E2;
    }

    .stTextInput > div > div > input:focus-visible {
        outline: none;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown("<h1 style='text-align: center;'>💬 Prompt Breaker (Flash Edition)</h1>", unsafe_allow_html=True)

# === Session Setup ===
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
    st.session_state.history = ""
    st.session_state.model = None
    st.session_state.system_prompt = ""

# === Prompt Input ===
prompt = st.text_area("✍️ Enter your character prompt (system instruction):", value=st.session_state.system_prompt)

# === Initialize model only if prompt changes ===
if prompt.strip() and (prompt != st.session_state.system_prompt or st.session_state.chat_session is None):
    st.session_state.system_prompt = prompt
    st.session_state.model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        system_instruction=system_instruction+prompt
    )
    st.session_state.chat_session = st.session_state.model.start_chat(history=[])
    st.session_state.history = ""

# === Display History ===
st.markdown("<div class='chat-box'>{}</div>".format(
    st.session_state.history.replace("\n", "<br>")
), unsafe_allow_html=True)

# === Get AI Response ===
def ai_response(user_input):
    response = st.session_state.chat_session.send_message(user_input)
    model_response = response.text
    st.session_state.chat_session.history.append({"role": "user", "parts": [user_input]})
    st.session_state.chat_session.history.append({"role": "model", "parts": [model_response]})
    return model_response

# === Input + Trigger ===
# Clear input safely using a key toggle
def on_submit():
    st.session_state.submitted = True
    st.session_state.input_to_send = st.session_state.user_input
    st.session_state.user_input = ""  # Clear input immediately

# Input box — text will clear after Enter
user_input = st.text_input("💬 Try to break the character:", key="user_input", on_change=on_submit)

# Handle submission
if st.session_state.get("submitted", False):
    user_msg = st.session_state.get("input_to_send", "").strip()

    if user_msg:
        reply = ai_response(user_msg)
        st.session_state.history += f"\nYou: {user_msg}\nAI: {reply}"

    st.session_state.submitted = False
    st.session_state.input_to_send = ""
    st.rerun()
