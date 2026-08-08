from langchain_core.documents import Document
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from pdf2image import convert_from_path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import time
import base64
from langchain_core.messages import HumanMessage

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
        image_name = f"{os.path.splitext(pdf)[0]}_page_{i+1}.png"
        image_path = os.path.join(TEMP_IMAGES_DIR,image_name)

        page.save(image_path,"PNG")
        saved_paths.append(image_path)

    print(f"succesfully saved {len(saved_paths)} images to {TEMP_IMAGES_DIR}")

    return saved_paths

def summery(saved_paths):
    summary_list = []
    
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    for image_path in saved_paths:

        with open(image_path,"rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text":"You are a financial analyst. Analyze this image extracted from a financial document. Provide a highly detailed summary of any charts, tables, graphs, or key metrics present. If it is just a standard text page, summarize the main point."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_data}"}
                }
            ]
        )
        summary = llm.invoke([message]).content
        summary_list.append(summary)

        time.sleep(4)
        print(f"done page")

    return summary_list

def pdf_to_chroma(pdf : str,summary_list: list):
    """ extracts text using pypdfloader,chunk it and stores in chroma db"""
    pdf_path = os.path.join(TEMP_UPLOADS_DIR,pdf)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"not found file on path {pdf_path}")

    print(f"converting {pdf} into vectors")

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 2000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(documents)
    summary_docs = []

    for i,item in enumerate(summary_list):
        if isinstance(item, list):
            # Extracts the text from the dictionary block
            page_text = " ".join([block.get("text", "") for block in item if isinstance(block, dict)])
        else:
            # Fallback to string conversion
            page_text = str(item)
        doc = Document(
            page_content=page_text,
            metadata={
                "source": pdf,
                "page": i+1,
                "type": "image_summary"
            }
        )
        summary_docs.append(doc)

    chunks = chunks + summary_docs

    if not chunks:
        raise ValueError("could not extract any readable text or images from pdf")
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
    saved_image_path = extract_images(sample_file)
    summery_generate = summery(saved_image_path)
    pdf_to_chroma(sample_file,summery_generate)
