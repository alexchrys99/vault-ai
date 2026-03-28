# --- THE LINUX SQLITE FIX ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# ----------------------------

import os
import shutil
import sqlite3
import bcrypt
from fastapi import FastAPI, UploadFile, Form, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

app = FastAPI(title="Corporate RAG API - Secure & Conversational")

# --- AI Setup ---
OLLAMA_URL = "http://192.168.142.1:11434"
llm = OllamaLLM(model="llama3.2:latest", base_url=OLLAMA_URL)
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_URL)
os.makedirs("temp_uploads", exist_ok=True)

# --- Security & Database Setup ---
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
conn.commit()

# --- Pydantic Models ---
class AuthRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    user_id: str
    question: str
    chat_history: List[Dict[str, str]] = []

# --- Authentication Endpoints (USING RAW BCRYPT) ---
@app.post("/register")
async def register(request: AuthRequest):
    # Hash the password directly
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), salt).decode('utf-8')
    
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (request.username, hashed_password))
        conn.commit()
        return {"status": "success", "message": "User registered successfully!"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists.")

@app.post("/login")
async def login(request: AuthRequest):
    c.execute("SELECT password FROM users WHERE username=?", (request.username,))
    row = c.fetchone()
    
    # Check the password directly
    if row and bcrypt.checkpw(request.password.encode('utf-8'), row[0].encode('utf-8')):
        return {"status": "success", "message": "Login successful!"}
    raise HTTPException(status_code=401, detail="Invalid username or password.")

# --- RAG Endpoints ---
@app.post("/upload")
async def upload_document(user_id: str = Form(...), file: UploadFile = Form(...)):
    try:
        file_path = f"temp_uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        if file.filename.endswith(".pdf"): loader = PyPDFLoader(file_path)
        else: loader = TextLoader(file_path)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(docs)
        for chunk in chunks:
            chunk.metadata["user_id"] = user_id 
            
        Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory="./chroma_db")
        os.remove(file_path)
        return {"status": "success", "message": f"Document secured for {user_id}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_documents(request: ChatRequest):
    vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    retriever = vector_db.as_retriever(search_kwargs={'filter': {'user_id': request.user_id}})
    
    system_prompt = (
        "You are a secure corporate AI assistant. Use the following context to answer the user's question. "
        "If you don't know the answer, say 'I do not have access to that information.'\n\n"
        "Context: {context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    formatted_history = [(msg["role"], msg["content"]) for msg in request.chat_history]
    
    response = rag_chain.invoke({
        "input": request.question,
        "chat_history": formatted_history
    })
    return {"answer": response['answer']}
