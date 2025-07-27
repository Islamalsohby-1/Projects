import streamlit as st
from chat_client import ChatClient
import os
import json
from datetime import datetime

def main():
    """Streamlit dashboard for secure chat application."""
    st.set_page_config(page_title="Secure Chat", layout="wide")
    st.title("🔒 Secure Chat Application")
    
    # Initialize session state
    if 'client' not in st.session_state:
        st.session_state.client = None
        st.session_state.chat_log = []
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        username = st.text_input("Username", value="User")
        host = st.text_input("Server Host", value="127.0.0.1")
        port = st.number_input("Server Port", value=12345, min_value=1024, max_value=65535)
        key_file = st.file_uploader("Upload Private Key (optional)", type="pem")
        pub_key_file = st.file_uploader("Upload Public Key (optional)", type="pem")
        
        if st.button("Connect to Server"):
            if key_file and pub_key_file:
                with open(f"{username}_private.pem", "wb") as f:
                    f.write(key_file.read())
                with open(f"{username}_public.pem", "wb") as f:
                    f.write(pub_key_file.read())
            
            st.session_state.client = ChatClient(host, port, username)
            try:
                st.session_state.client.connect()
                st.session_state.client.start()
                st.success("Connected to server!")
            except Exception as e:
                st.error(f"Connection failed: {e}")
        
        if st.session_state.client and st.button("Disconnect"):
            st.session_state.client.stop()
            st.session_state.client = None
            st.success("Disconnected from server")

    # Main chat interface
    if st.session_state.client:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.header("Chat Window")
            message = st.text_area("Type your message or paste emoji 😊", height=100)
            file = st.file_uploader("Send File (encrypted)", type=["txt"])
            
            if st.button("Send"):
                if message.strip():
                    st.session_state.client.send_message(message)
                    st.session_state.client.save_log()
                if file:
                    file_path = f"temp_{file.name}"
                    with open(file_path, "wb") as f:
                        f.write(file.read())
                    st.session_state.client.send_message(file_path, is_file=True)
                    st.session_state.client.save_log()
                    os.remove(file_path)
            
            # Display chat history
            st.subheader("Chat History")
            for msg in st.session_state.client.chat_log[-100:]:
                st.write(f"[{msg['timestamp']}] {msg['sender']}: {msg['message']}")

        with col2:
            st.header("Status")
            st.write(f"Username: {username}")
            st.write(f"Connected to: {host}:{port}")
            st.write("Encryption: RSA + AES-256 (CBC)")
            st.write("Integrity: HMAC-SHA256")
            if st.button("Export Chat Log"):
                st.session_state.client.save_log()
                with open(f"{username}_chat_log.json", "r") as f:
                    st.download_button(
                        label="Download Chat Log",
                        data=f.read(),
                        file_name=f"{username}_chat_log.json",
                        mime="application/json"
                    )
    else:
        st.warning("Please connect to the server to start chatting.")

if __name__ == '__main__':
    main()