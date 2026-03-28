import streamlit as st
import requests

API_URL = "http://api:8000"

st.set_page_config(page_title="Vault AI - Secure RAG", page_icon="🔒", layout="wide")

# --- INITIALIZE SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🔒 Vault AI: Enterprise Document Intelligence")

# --- LOGIN / REGISTER SCREEN ---
if not st.session_state.logged_in:
    st.markdown("### Welcome to the Secure Vault. Please authenticate.")
    tab1, tab2 = st.tabs(["Log In", "Register New User"])
    
    with tab1:
        with st.form("login_form"):
            log_user = st.text_input("Username")
            log_pass = st.text_input("Password", type="password")
            if st.form_submit_button("Enter Vault"):
                res = requests.post(f"{API_URL}/login", json={"username": log_user, "password": log_pass})
                if res.status_code == 200:
                    st.session_state.logged_in = True
                    st.session_state.user_id = log_user
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")
                    
    with tab2:
        with st.form("register_form"):
            reg_user = st.text_input("Choose a Username")
            reg_pass = st.text_input("Choose a Password", type="password")
            if st.form_submit_button("Register"):
                res = requests.post(f"{API_URL}/register", json={"username": reg_user, "password": reg_pass})
                if res.status_code == 200:
                    st.success("✅ Registration successful! You can now log in.")
                else:
                    st.error(f"❌ {res.json().get('detail', 'Registration failed')}")

# --- MAIN DASHBOARD (Only visible if logged in) ---
else:
    with st.sidebar:
        st.header(f"👤 Welcome, {st.session_state.user_id}")
        if st.button("🚪 Log Out", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.user_id = ""
            st.session_state.messages = [] # Clear chat on logout
            st.rerun()
        
        st.divider()
        st.header("📄 Secure Upload")
        uploaded_file = st.file_uploader("Upload to your private vault", type=["pdf", "txt"])
        
        if st.button("Encrypt & Upload", type="primary"):
            if uploaded_file:
                with st.spinner("Embedding securely into ChromaDB..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {"user_id": st.session_state.user_id}
                    res = requests.post(f"{API_URL}/upload", files=files, data=data)
                    if res.status_code == 200:
                        st.success("✅ File securely embedded!")
                    else:
                        st.error("❌ Upload failed.")
            else:
                st.warning("Please select a file first.")

    st.subheader("💬 Secure Conversational Chat")
    st.caption("The AI now remembers your previous messages in this session!")

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Ask API (Pass the chat history, excluding the current prompt)
        with st.chat_message("assistant"):
            with st.spinner("Searching your secure vault..."):
                chat_history_to_send = st.session_state.messages[:-1] 
                payload = {
                    "user_id": st.session_state.user_id,
                    "question": prompt,
                    "chat_history": chat_history_to_send
                }
                
                try:
                    res = requests.post(f"{API_URL}/chat", json=payload)
                    if res.status_code == 200:
                        answer = res.json()["answer"]
                    else:
                        answer = f"⚠️ API Error: {res.text}"
                except Exception as e:
                    answer = "⚠️ Could not connect to the FastAPI backend."

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
