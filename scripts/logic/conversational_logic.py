# scripts/logic/conversational_logic.py

import os
from typing import List

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


# ======================================================
#                  DEBUGGING RETRIEVER
# ======================================================
class DebuggingRetriever(BaseRetriever):
    base_retriever: BaseRetriever
    debug_flag: bool = False

    # FIX: REQUIRED FOR PYDANTIC VALIDATION
    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "allow",
    }

    def __init__(
        self,
        base_retriever: BaseRetriever,
        debug_flag: bool = False,
        **kwargs,
    ):
        # ensure pydantic sees these fields
        super().__init__(base_retriever=base_retriever, debug_flag=debug_flag, **kwargs)
        self.base_retriever = base_retriever
        self.debug_flag = debug_flag

    def _get_relevant_documents(self, query: str, **kwargs) -> List[Document]:
        """Synchronous document retrieval."""
        docs = self.base_retriever.get_relevant_documents(query)

        if self.debug_flag:
            print("\n========== RETRIEVED DOCUMENTS ==========\n")
            for idx, doc in enumerate(docs, start=1):
                print(f"[Doc {idx}]")
                print("Source:", doc.metadata.get("source", "N/A"))
                print("Page  :", doc.metadata.get("page", "N/A"))
                print(doc.page_content[:500], "...\n")
            print("=========================================\n")

        return docs

    async def _aget_relevant_documents(self, query: str, **kwargs):
        """Async version (not used)."""
        raise NotImplementedError


# ======================================================
#              LOAD LOCAL RAG CHAIN
# ======================================================
def load_local_chain_with_guardrails(
    llm_model_name: str,
    embedding_model_name: str,
    vector_db_path: str,
    debug_retrieval: bool = False,
):
    """
    Loads and configures the local RAG chain:
    - FAISS Vector Store
    - HuggingFace Embeddings
    - Ollama LLM (Gemma 2B)
    - Guardrail prompt
    """

    # -------------------------
    # 1️⃣ Load Embeddings
    # -------------------------
    print(f"Loading embedding model: {embedding_model_name}...")
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

    # -------------------------
    # 2️⃣ Load FAISS Vector Store
    # -------------------------
    if not os.path.exists(vector_db_path):
        raise FileNotFoundError(f"FAISS vector store missing at: {vector_db_path}")

    print(f"Loading FAISS vector store from {vector_db_path}...")
    db = FAISS.load_local(
        vector_db_path,
        embeddings,
        allow_dangerous_deserialization=True,
    )

    # Retriever
    base_retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5, "fetch_k": 10},
    )

    retriever = DebuggingRetriever(
        base_retriever=base_retriever,
        debug_flag=debug_retrieval,
    )

    # -------------------------
    # 3️⃣ Initialize Ollama LLM
    # -------------------------
    print(f"Initializing local Ollama LLM: {llm_model_name}...")
    llm = Ollama(model=llm_model_name, temperature=0.1)

    # -------------------------
    # 4️⃣ Security Guardrail Prompt
    # -------------------------
    template = """
You are a secure VIT HR Policy Bot. You must answer ONLY using the HR policy context provided.

Rules:
- If the answer is completely provided in the context → give a direct answer.
- If partial info exists → state what's available + say:
  "I am sorry, the full details are not available in the provided HR policy document."
- If NOTHING in context is relevant → say:
  "I am sorry, that information is not in the HR policy document."
- DO NOT use external knowledge.
- DO NOT guess or assume anything.

Context:
{context}

Question:
{question}

Answer:
"""

    # IMPORTANT: RetrievalQA internally passes "question", not "query", to the prompt
    QA_PROMPT = PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )

    # -------------------------
    # 5️⃣ Build RetrievalQA Chain
    # -------------------------
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        # Outer chain input key (what you call from app.py)
        input_key="query",
        output_key="result",
        return_source_documents=False,
        chain_type_kwargs={"prompt": QA_PROMPT},
    )

    return qa_chain
