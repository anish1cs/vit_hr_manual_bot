# scripts/build_index.py
# This script runs 100% LOCALLY and does NOT use any APIs.

import os
# --- THIS IS THE CORRECTED IMPORT PATH ---
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# --- Configuration ---
PROCESSED_TEXT_PATH = "data/processed/cleaned_policy.txt"
VECTOR_STORE_PATH = "data/vector_store"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# ---------------------

def main():
    print("--- Starting FAISS index creation (using local model) ---")

    print(f"1. Loading cleaned text from: {PROCESSED_TEXT_PATH}")
    if not os.path.exists(PROCESSED_TEXT_PATH):
        print(f"Error: Cleaned text file not found at {PROCESSED_TEXT_PATH}")
        print("Please run 'python scripts/clean_and_prepare.py' first.")
        return
        
    with open(PROCESSED_TEXT_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    print("2. Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    print(f"✅ Created {len(chunks)} chunks.")

    print(f"3. Initializing local embeddings from: {EMBEDDING_MODEL}")
    print("(This may take a moment to download the model on first run...)")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'} # Force running on CPU
    )
    print("✅ Embeddings model initialized.")

    print("4. Creating FAISS vector store from chunks...")
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)
    print("✅ Vector store created in memory.")

    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    
    print(f"5. Saving FAISS index to disk at: {VECTOR_STORE_PATH}")
    vectorstore.save_local(VECTOR_STORE_PATH)

    print("\n--- Success! ---")
    print("✅ FAISS index was built and saved successfully.")

if __name__ == "__main__":
    main()