# Dynamic Multi-Modal Financial Document Assistant

A Streamlit-based AI application that allows you to upload financial PDFs (like 10-Qs or earnings reports) and chat with them. Unlike standard RAG systems that only read text, this assistant uses Google's Gemini 1.5 Flash to dynamically extract, read, and understand charts, graphs, and tables embedded in your documents.

Built entirely using a 100% free tech stack (Google Gemini free tier + open-source tools).

## Features

* **Dynamic File Uploads:** Upload any PDF directly through the Streamlit UI.
* **Multi-Modal RAG:** Parses both standard text and image-based charts/tables.
* **Intelligent Image Summarization:** Uses Gemini 1.5 Flash to generate context-aware summaries of financial charts.
* **Local Vector Storage:** Uses ChromaDB for fast, private, and local vector search.
* **Automated Cleanup:** Manages temporary file storage efficiently during the active session.

## Tech Stack

* **UI Framework:** [Streamlit](https://streamlit.io/)
* **Orchestration:** [LangChain](https://python.langchain.com/)
* **LLM & Vision Model:** [Google Gemini 1.5 Flash](https://ai.google.dev/)
* **Embeddings:** Google Generative AI Embeddings
* **Vector Database:** [ChromaDB](https://www.trychroma.com/)
* **PDF Processing:** `pdf2image`, `pypdf`, and `poppler`

## Folder Structure

```text
dynamic-multimodal-rag/
│
├── .env                      # Stores your GEMINI_API_KEY
├── .gitignore                
├── requirements.txt          
├── README.md                 
│
├── data/                     
│   ├── temp_uploads/         # Temporarily stores the uploaded PDF
│   ├── temp_images/          # Temporarily stores extracted charts (PNGs)
│   └── chroma_db/            # Local persistent vector database
│
├── src/                      
│   ├── __init__.py
│   ├── file_handler.py       # Handles saving/deleting temp files
│   ├── document_processor.py # Extracts text/images and generates Gemini summaries
│   └── rag_chain.py          # LCEL logic for ChromaDB retrieval and Gemini Q&A
│
└── app.py                    # Streamlit UI and session state manager