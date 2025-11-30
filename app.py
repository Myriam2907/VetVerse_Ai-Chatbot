import streamlit as st
import json
import sys
from pathlib import Path
from PIL import Image
import base64

# Import the chatbot (make sure free_rag_pipeline.py is in same directory)
try:
    from free_rag_pipeline import FreeVETChatbot
except ImportError:
    st.error("⚠️ Make sure 'free_rag_pipeline.py' is in the same directory!")
    st.stop()

# Page config
st.set_page_config(
    page_title="VetVerse 🐾 AI Assistant",
    page_icon="🐾",
    layout="wide"
)

# Function to convert image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Load images and convert to base64
try:
    background_image = get_base64_image("background.png")
except Exception as e:
    st.error(f"⚠️ Error loading image: {e}")
    st.info("Make sure 'sinouj.png' is in the same directory as this script!")
    st.stop()

# Custom CSS with background image
st.markdown(f"""
<style>
    /* Set background for the entire app */
    .stApp {{
        background-image: url("data:image/png;base64,{background_image}");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        min-height: 100vh;
    }}
    
    /* Add slight blur and overlay to main content area */
   .main .block-container {{
    background-color: rgba(255, 255, 255, 0.9);
    padding: 2rem;
    border-radius: 10px;
    backdrop-filter: blur(150px);
    max-width: 1200px;
    margin: 0 auto;
}}

    
    .main-header {{
        font-size: 2.5rem;
        font-weight: bold;
        color: #5C3A21;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(255,255,255,0.8);
    }}
    
    .emergency-box {{
        background-color: rgba(255, 235, 238, 0.95);
        border-left: 5px solid #D32F2F;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }}
    
    .source-box {{
        background-color: rgba(227, 242, 253, 0.95);
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        border-left: 3px solid #1976D2;
    }}
    
    .disclaimer {{
        background-color: rgba(255, 243, 224, 0.95);
        padding: 1rem;
        border-radius: 5px;
        margin-top: 1rem;
        font-size: 0.9rem;
    }}
    
    /* Chat messages styling */
    .stChatMessage {{
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: rgba(248, 249, 250, 0.95);
        backdrop-filter: blur(5px);
    }}
    
    /* Chat input styling */
    .stChatInputContainer {{
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize chatbot 
@st.cache_resource
def load_chatbot():
    try:
        return FreeVETChatbot()
    except Exception as e:
        st.error(f"Error loading chatbot: {e}")
        st.info("Make sure you have:\n1. Dataset file in the same folder\n2. Ollama installed and running\n3. Model downloaded: ollama pull llama3.2:3b")
        return None

if "history" not in st.session_state:
    st.session_state.history = []



if st.button("🔄 New Chat"):
    st.session_state.messages = []  

# Header
st.markdown('<div class="main-header">VetVerse 🐾 AI Assistant</div>', unsafe_allow_html=True)
st.markdown("**Free, AI-Powered Pet Health Information** • Powered by Local LLM")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    This chatbot provides general veterinary information using:
    - **100% FREE** - No API costs
    - **Local LLM** - Runs on your machine
    - **RAG Architecture** - Grounded in veterinary knowledge
    """)
    
    st.divider()
    
    st.header("⚙️ System Status")
    chatbot = load_chatbot()
    if chatbot:
        st.success("✅ Chatbot loaded")
    else:
        st.error("❌ Chatbot not loaded")
    
    st.divider()
    
    st.header("📋 Example Questions")
    examples = [
        "My dog ate chocolate",
        "How often should I feed my cat?",
        "Why is my dog scratching?",
        "Cat not eating for 2 days",
        "Puppy vomiting"
    ]
    
    for example in examples:
        if st.button(example, key=example):
            st.session_state['example_question'] = example

    st.divider()
    
    st.markdown("""
    **⚠️ Disclaimer**
    
    This tool provides general information only. 
    Always consult a licensed veterinarian for:
    - Emergencies
    - Diagnosis
    - Treatment plans
    - Medical advice
    """)

# Main chat interface
if chatbot:
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📚 View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"""
                        <div class="source-box">
                        <strong>Source {i}:</strong> {source['question']}<br>
                        <small>Urgency: {source['urgency']} | Species: {source['species']}</small>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Handle example questions from sidebar
    if 'example_question' in st.session_state:
        user_input = st.session_state.pop('example_question')
    else:
        user_input = st.chat_input("Ask a pet health question...")
    
    # Process user input
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Add to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Get chatbot response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    output = chatbot.chat(user_input)
                    
                    # Display emergency warning if needed
                    if output['is_emergency']:
                        st.markdown("""
                        <div class="emergency-box">
                        ⚠️ <strong>EMERGENCY SITUATION DETECTED</strong><br>
                        Please contact your veterinarian or emergency vet clinic immediately!
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Display answer
                    st.markdown(output['answer'])
                    
                    # Display sources
                    with st.expander("📚 View Sources"):
                        for i, source in enumerate(output['sources'], 1):
                            st.markdown(f"""
                            <div class="source-box">
                            <strong>Source {i}:</strong> {source['question']}<br>
                            <small>Urgency: {source['urgency']} | Species: {source['species']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": output['answer'],
                        "sources": output['sources'],
                        "is_emergency": output['is_emergency']
                    })
                
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.info("Make sure Ollama is running: `ollama serve`")
    
    # Footer disclaimer
    st.markdown("""
    <div class="disclaimer">
    <strong>⚠️ Important Disclaimer:</strong> This chatbot provides general information only and is not a substitute 
    for professional veterinary advice, diagnosis, or treatment. Always seek the advice of your veterinarian 
    with any questions about your pet's health. In case of emergency, contact your vet or emergency animal hospital immediately.
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("⚠️ Chatbot failed to load. Please check the setup instructions in the sidebar.")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🐕 Dogs")
with col2:
    st.caption("🐱 Cats")
with col3:
    st.caption("🆓 100% Free")