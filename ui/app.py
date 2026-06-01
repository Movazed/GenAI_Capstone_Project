import streamlit as st
import sys
import os
import uuid  # <-- ADDED for generating unique session IDs

ui_dir = os.path.dirname(__file__)

root_dir = os.path.abspath(os.path.join(ui_dir, '..'))
orchestration_dir = os.path.join(root_dir, 'orchestration')

if root_dir not in sys.path:
    sys.path.append(root_dir)
if orchestration_dir not in sys.path:
    sys.path.append(orchestration_dir)

from orchestration.graph import app as telecom_graph

st.set_page_config(page_title="Prodapt AI Agent", page_icon="📡", layout="centered")

st.title("📡 Prodapt Telecom AI Assistant")
st.markdown("Welcome to the autonomous support center. Ask about **outages**, **billing disputes**, or **SLA policies**.")

# Check if this user already has a session ID. If not, generate a new UUID.
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help you today?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Analyzing request and routing to specialists..."):
            try:
                # <-- ADDED config block with the unique thread_id
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                
                # <-- MODIFIED invoke to include the config
                final_state = telecom_graph.invoke({"customer_message": prompt}, config=config)
                agent_response = final_state.get('final_email', "Error: No response generated.")
            except Exception as e:
                agent_response = f"**System Error:** Could not reach the backend. Are your ADK ports 8001 and 8002 running?\n\nDetails: {str(e)}"

        st.markdown(agent_response)
        st.session_state.messages.append({"role": "assistant", "content": agent_response})