from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import os
from operator import itemgetter
from langchain_chroma import Chroma
from langchain_core.runnables import RunnableParallel,RunnablePassthrough

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR,"data")

CHORMA_DB_DIR = os.path.join(DATA_DIR,"chroma_db")

def get_retriver():
    """connect local db and returns a retriver."""
    embedding = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")

    vector_store = Chroma(
        persist_directory=CHORMA_DB_DIR,
        embedding_function=embedding
    )

    return vector_store.as_retriever(search_kwargs={"k": 5})

def format_docs(docs):
    """Formats rerieved document chunks into a single string."""

    return "\n\n".join(doc.page_content for doc in docs)

def generate_answer(question: str,chat_history: list) -> str:
    """for user's question answer"""

    formatted_history = "\n".join(
        [f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history[:-1]]
    )
    if not formatted_history:
        formatted_history = "No previous conversation."

    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2)

    retriever = get_retriver()

    template = """You are a highly capable financial assistant analyzing a document.
    Use the following retrieved context from the document to answer the user's question. 
    If you cannot find the answer in the context, explicitly state that you don't know based on the provided document.
    Keep your answer concise, accurate, and professional.

    Context: {context}

    Question: {question}

    Answer:"""

    parser = StrOutputParser()
    prompt = PromptTemplate.from_template(template)

    rag_chain  = RunnableParallel({
        'context' : itemgetter("question") | retriever | format_docs,
        'question': itemgetter("question"),
        "chat_history":itemgetter("chat_history")
    })

    final_rag_chain = rag_chain | prompt | llm | parser

    return final_rag_chain.invoke({
        "question":question,
        "chat_history" : formatted_history
    })