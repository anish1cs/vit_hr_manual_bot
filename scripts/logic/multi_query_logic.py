# scripts/logic/multi_query_logic.py

import os
import logging
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
# --- CORRECTED IMPORTS ---
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.retrievers.multi_query import MultiQueryRetriever

# Set up logging to see the generated queries
logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

load_dotenv()
VECTOR_STORE_PATH = "data/vector_store"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def create_multi_query_chain():
    """
    Builds and returns a RetrievalQA chain that uses the MultiQueryRetriever.
    """
    print("🤖 Loading Gemini models and building Multi-Query chain...")

    # --- PROMPT for the final answer generation ---
    qa_prompt_template = """
    You are an HR Policy Assistant. Use the following pieces of context to answer the question at the end.
    Provide a comprehensive answer by synthesizing all relevant information from the context.
    If you don't know the answer from the context, just say that you cannot find the information in the policy document.

    Context: {context}

    Question: {question}

    Helpful Answer:
    """
    QA_PROMPT = PromptTemplate(template=qa_prompt_template, input_variables=["context", "question"])

    # --- Initialize Models and Retriever ---
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'}
    )
    vectorstore = FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # --- FINAL FIX: Switched to the universally stable 'gemini-pro' model ---
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.1)

    # --- The Multi-Query Retriever ---
    retriever_with_generated_queries = MultiQueryRetriever.from_llm(
        retriever=base_retriever, llm=llm
    )

    # --- The final QA chain ---
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever_with_generated_queries,
        chain_type_kwargs={"prompt": QA_PROMPT}
    )

    print("✅ Gemini Multi-Query chain is ready.")
    return qa_chain