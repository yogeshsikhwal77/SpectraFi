import streamlit as st
import os
from src.file_handler import save_file,clear_file
from src.document_processor import extract_images,pdf_to_chroma,summery
from src.rag_chain import generate_answer
st.set_page_config(page_title="spectrafi")

st.title("Multi-model Financial document assitant")

st.markdown("Upload your 10-Qs, earnings reports, or any financial PDF to extract, read, and chat with charts, graphs, and text")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_processed" not in st.session_state:
    st.session_state.is_processed = False
if "current_file" not in st.session_state:
    st.session_state.current_file = None


with st.sidebar:
    st.header("Document Upload")
    uploaded_file = st.file_uploader("upload a financial pdf",type=["pdf"])

    if uploaded_file is not None and not st.session_state.is_processed:
        with st.spinner("saving and processing document"):
            filename = save_file(uploaded_file)
            st.session_state.current_file = filename

            st.info("Extracting charts and tables as images....")
            saved_image_path = extract_images(filename)

            st.info("Generating intelligent summaries for images...")
            # 2. Pass the image paths to your summery function
            summary_list = summery(saved_image_path)
            
            st.info("vectorizing documet text into chromadb....")
            pdf_to_chroma(filename,summary_list)

            st.session_state.is_processed = True
            st.success("Documents processed successfully: now we can chat")

    if st.button("clear Data & reset chat"):
        clear_file()
        st.session_state.messages = []
        st.session_state.is_processed = False
        st.session_state.current_file = None
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("ask a question about the uploaded document...."):
    if not st.session_state.is_processed:
        st.warning("please upload a file")
    else:
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role":"user","content":prompt})

        with st.chat_message("assistant"):
            with st.spinner("Analyzing document..."):
                
                response = generate_answer(prompt,st.session_state.messages)
                st.markdown(response)
        
        # Save assistant response to state
        st.session_state.messages.append({"role": "assistant", "content": response})