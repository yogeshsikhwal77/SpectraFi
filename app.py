import streamlit as st
import os
from src.file_handler import save_file, clear_file
from src.document_processor import extract_images, pdf_to_chroma, summery
from src.rag_chain import generate_answer

# Page Configuration
st.set_page_config(
    page_title="SpectraFi | Financial Document Assistant",
    page_icon="📈",
    layout="wide"
)

# Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_processed" not in st.session_state:
    st.session_state.is_processed = False
if "current_file" not in st.session_state:
    st.session_state.current_file = None

# App Header
st.title("📈 SpectraFi")
st.caption("Multimodal Financial Document Assistant — Upload 10-Qs, earnings reports, or filings to analyze text, charts, and tables.")

# Document Upload and Management Section (Top Card)
with st.expander("📁 Document Control & Upload", expanded=not st.session_state.is_processed):
    col1, col2 = st.columns([3, 1])

    with col1:
        uploaded_file = st.file_uploader("Upload a financial PDF", type=["pdf"])

    with col2:
        st.write("**Status & Actions**")
        if st.session_state.is_processed:
            st.success(f"**Loaded:** `{os.path.basename(st.session_state.current_file)}`")
        else:
            st.info("No document loaded.")

        if st.button(" Clear Data & Reset Chat", use_container_width=True):
            clear_file()
            st.session_state.messages = []
            st.session_state.is_processed = False
            st.session_state.current_file = None
            st.rerun()

    # Processing Pipeline (Triggers inside the main block)
    if uploaded_file is not None and not st.session_state.is_processed:
        with st.status("Processing Document...", expanded=True) as status:
            st.write(" Saving uploaded file...")
            filename = save_file(uploaded_file)
            st.session_state.current_file = filename

            st.write(" Extracting charts and tables as images...")
            saved_image_path = extract_images(filename)

            st.write(" Generating multimodal image summaries...")
            summary_list = summery(saved_image_path)
            
            st.write(" Vectorizing content into ChromaDB...")
            pdf_to_chroma(filename, summary_list)

            st.session_state.is_processed = True
            status.update(label="Document processed successfully!", state="complete", expanded=False)
            st.rerun()

st.divider()

# Chat Area Container
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# User Chat Input
if prompt := st.chat_input("Ask a question about financial metrics, tables, or charts..."):
    if not st.session_state.is_processed:
        st.warning("Please upload a PDF document in the panel above first.")
    else:
        # Display user message
        st.chat_message("user", avatar="👤").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate Assistant response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analyzing document content..."):
                response = generate_answer(prompt, st.session_state.messages)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})