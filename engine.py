# --- THE LINUX SQLITE FIX ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# ----------------------------

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Connect to your Windows Machine
OLLAMA_URL = "http://192.168.142.1:11434"
print("📡 Connecting to Windows AI Server...")

llm = OllamaLLM(model="llama3.2:latest", base_url=OLLAMA_URL)
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_URL)

# 2. Load and Chunk the Document
print("📄 Loading secret_contract.txt...")
loader = TextLoader("secret_contract.txt")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(docs)

# 3. Create the Vector Database (ChromaDB)
print("🧠 Building Vector Database...")
vector_db = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory="./chroma_db")
retriever = vector_db.as_retriever()

# 4. Create the AI Brain Prompt
system_prompt = (
    "You are a highly secure corporate AI assistant. "
    "Use the following retrieved context to answer the user's question. "
    "If you don't know the answer, say that you don't know. Keep it concise.\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# 5. Connect it all together
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# 6. Ask the Question!
question = "What is Alexander's base salary and bonus structure?"
print(f"\n🗣️ Question: {question}")
print("⏳ Thinking...\n")

response = rag_chain.invoke({"input": question})
print(f"🤖 Llama 3.2 Answer: {response['answer']}")
