import os
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
import vconsoleprint
load_dotenv()

# ---------------- Embedding Model ----------------
embedding_model = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")

# ---------------- Document Fetcher ----------------
def document_fetcher(docs: str = "docs"):
    """Fetch all files documents from docs folder"""

    if not os.path.exists(docs):
        raise FileNotFoundError(f"Docs folder not found at: {docs}")

    loader = DirectoryLoader(
        path=docs,
        glob="**/*",
        loader_cls=UnstructuredFileLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )

    documents = loader.load()
    return documents


# ---------------- Chunking ----------------
def chunking_documents(documents, chunk_size: int = 200, chunk_overlap: int = 0):
    """Split documents into chunks"""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = splitter.split_documents(documents)
    return chunks


def create_vector_store(path: str = "db"):
    """Create or load Chroma vector database"""

    if os.path.exists(path):
        print("Existing DB found. Loading...")
        vectorstore = Chroma(
            persist_directory=path,
            embedding_function=embedding_model,
            collection_metadata={"hnsw:space": "cosine"},
        )
        return vectorstore

    print("Creating new vector DB...")
    documents = document_fetcher("docs")
    chunks = chunking_documents(documents)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=path,
        collection_metadata={"hnsw:space": "cosine"},
    )

    return vectorstore


def create_retreiver(k=3):
    vectorstore = create_vector_store("db")
    return vectorstore.as_retriever(search_kwargs={"k":k})



if __name__ == "__main__":
    create_retreiver()
