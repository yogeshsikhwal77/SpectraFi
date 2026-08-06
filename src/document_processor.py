from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from pdf2image import convert_from_path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import time

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR,"data")
TEMP_UPLOADS_DIR = os.path.join(DATA_DIR, "temp_uploads")
TEMP_IMAGES_DIR = os.path.join(DATA_DIR, "temp_images")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")

def extract_images(pdf: str):
    """Extracts pages from a pdf as images and saves them to data/temp_images/"""

    pdf_path = os.path.join(TEMP_UPLOADS_DIR,pdf)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"not found file on path {pdf_path}")

    print(f"Converting {pdf} to images....")
    
    print("...................converting................")
    pages = convert_from_path(pdf_path, poppler_path=r'C:\poppler\Library\bin')

    saved_paths = []

    for i,page in enumerate(pages):
        image_name = f"{os.path.splitext(pdf)[0]}_page_{i+1}.jpg"
        image_path = os.path.join(TEMP_IMAGES_DIR,image_name)

        page.save(image_path,"JPEG")
        saved_paths.append(image_path)

    print(f"succesfully saved {len(saved_paths)} images to {TEMP_IMAGES_DIR}")

    return saved_paths

def pdf_to_chroma(pdf : str):
    """ extracts text using pypdfloader,chunk it and stores in chroma db"""
    pdf_path = os.path.join(TEMP_UPLOADS_DIR,pdf)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"not found file on path {pdf_path}")

    print(f"converting {pdf} into vectors")

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap=100
    )

    chunks = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR
    )

    print(f"successfully processed {len(chunks)} text chunks into chroma db")

    return vector_store


if __name__ == "__main__":
    os.makedirs(TEMP_UPLOADS_DIR, exist_ok=True)
    os.makedirs(TEMP_IMAGES_DIR, exist_ok=True)
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)

    sample_file = "cslab.pdf"
    extract_images(sample_file)
    pdf_to_chroma(sample_file)
