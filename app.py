import streamlit as st
from openai import OpenAI
import os

# ---------- Page Config ----------
st.set_page_config(
    page_title="Wexer Chatbot",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ---------- Title ----------
st.title("⚡ Wexer Chatbot")
st.caption("Powered by Grok • Live web search • Legal & ethical security discussion allowed")

# ---------- API Key ----------
api_key = None

# Try Streamlit secrets first, then environment variable
try:
    api_key = st.secrets["XAI_API_KEY"]
except:
    api_key = os.getenv("XAI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Enter your xAI API Key", type="password", key="api_key_input")
    if not api_key:
        st.info("👉 Please enter your xAI API Key in the sidebar to start chatting.")
        st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1"
)

# ---------- Full System Prompt (one complete policy) ----------
SYSTEM_PROMPT = """
You are Wexer, a helpful, truthful, and slightly witty AI assistant.

You have live web search. Use it whenever the user needs up-to-date information and cite sources naturally.

### Security / Hacking Policy (this is the complete rule):
You MAY discuss:
- Ethical hacking and gray-hat concepts at a high level
- Bug bounty programs and responsible disclosure
- Legal frameworks (CFAA, computer crime laws, privacy laws, etc.)
- History of hacking and notable cases
- Defensive security, secure coding, and best practices
- Public tools and certifications (CEH, OSCP, CompTIA Security+, etc.)
- Theoretical and academic discussion of vulnerabilities

You MUST refuse when the user asks for:
- Step-by-step instructions on how to hack or gain unauthorized access
- Working exploit code or attack scripts
- Practical methods that could be used to commit a crime

If a request is borderline, stay on the legal and defensive side and explain why you cannot provide attack instructions.

### Other hard limits (never assist with):
- Child sexual content or exploitation
- Instructions for real-world violence or terrorism
- Manufacturing illegal drugs or weapons
- Fraud, scams, or theft methods
- Self-harm methods

Be clear, direct, and helpful. Keep answers well-structured.
"""

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# ---------- Display Chat History ----------
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ---------- Chat Input ----------
if prompt := st.chat_input("Message Wexer..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            response = client.chat.completions.create(
                model="grok-4.7",
                messages=st.session_state.messages,
                tools=[{"type": "web_search"}],
                tool_choice="auto",
                temperature=0.7,
                stream=True
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            # Save assistant reply
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as e:
            st.error(f"Error: {str(e)}")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Wexer Controls")

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        st.rerun()

    st.markdown("---")
    st.markdown("**Features**")
    st.markdown("- Live web search")
    st.markdown("- Streaming replies")
    st.markdown("- Legal / ethical security discussion")
    st.markdown("- Refuses illegal how-to instructions")

    st.markdown("---")
    st.caption("Wexer Chatbot • Powered by xAI Grok")
