
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# ==================================
# Load Environment Variables
# ==================================
load_dotenv()

# ==================================
# Load Documents
# ==================================
loader = TextLoader("docs/authentication.md")
documents = loader.load()

print(f"Documents Loaded: {len(documents)}")

# ==================================
# Chunk Documents
# ==================================
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)

chunks = text_splitter.split_documents(documents)

print(f"Total Chunks Created: {len(chunks)}")

# ==================================
# Create Embeddings
# ==================================
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# ==================================
# Create ChromaDB
# ==================================
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",
)

print("Vector Store Created Successfully!")
print(f"Stored {len(chunks)} chunks.")

