📘 HR Policy RAG Chatbot
(Flask + LangChain + FAISS + Ollama Gemma:2b — Fully Local AI Assistant)

This project is a fully local Retrieval-Augmented Generation (RAG) HR Policy Chatbot that answers questions strictly using the official VIT HR Manual. The entire system works offline, powered by:

🧠 Ollama Gemma:2b (local LLM)

🔍 FAISS for vector similarity search

📝 LangChain for retrieval + guardrails

🌐 Flask frontend with full chat UI

⚡ 100% privacy safe — no API calls
⚡ Works completely offline
⚡ Uses a secure guardrail prompt to prevent hallucination

🚀 Features
🧠 Fully Local RAG Chatbot

Runs entirely on your machine — no cloud, no API keys.

🔐 Strong Guardrail Prompt

The bot answers only from context, never guesses.

🔍 FAISS Vector Database

Searches the HR manual at high speed.

🧪 Debug Retriever

Optionally prints retrieved chunks in console.

💬 Modern Chat Interface

Includes:

Chat history

Clear all chats

Typing animation

LocalStorage persistence

Responsive UI (dark mode)

📁 Project Structure
vit_hr_manual_bot_testing/
│── app.py
│── requirements.txt
│── README.md
│── .gitignore

├── scripts/
│   ├── logic/
│   │   ├── conversational_logic.py
│   │   └── multi_query_logic.py
│   ├── clean_and_prepare.py
│   ├── build_index.py
│   └── start_chat.py

├── data/
│   ├── raw/
│   │   └── HR_POLICY_merged.pdf
│   ├── processed/
│   │   └── cleaned_policy.txt
│   └── vector_store/

├── templates/
│   └── index.html

└── static/
    ├── script.js
    └── style.css

🔧 Installation
1️⃣ Install Ollama

Download → https://ollama.com/download

Then pull the model:

ollama pull gemma:2b


Make sure Ollama is running:

ollama serve

2️⃣ Create a Virtual Environment
python -m venv .venv


Activate it:

Windows
.venv\Scripts\activate

macOS/Linux
source .venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

🧹 Step 1 — Clean the HR PDF

This generates a clean text file from the PDF.

python scripts/clean_and_prepare.py


Output saved at:

data/processed/cleaned_policy.txt

🧠 Step 2 — Build the FAISS Vector Store
python scripts/build_index.py


Creates:

data/vector_store/

▶ Step 3 — Run the Chatbot (Flask)
python app.py


Visit:

http://127.0.0.1:5000

🧩 How the RAG System Works
PDF → Clean Text → Chunking → Embeddings → FAISS Index → Retriever → LLM

Flow Diagram
HR Policy PDF
      │
(clean_and_prepare.py)
      ▼
Cleaned Text
      │
(build_index.py)
      ▼
FAISS Vector Store
      │
User Query
      ▼
Retriever (MMR)
      ▼
Guardrail Prompt
      ▼
Ollama Gemma 2b
      ▼
Final Answer

🐞 Debug Mode

Enable retrieved-chunk printing by setting:

DEBUG_RETRIEVAL = True

🧪 Test the Chain (without Flask)
from scripts.logic.conversational_logic import load_local_chain_with_guardrails

chain = load_local_chain_with_guardrails(
    llm_model_name="gemma:2b",
    embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
    vector_db_path="data/vector_store",
    debug_retrieval=True
)

print(chain.invoke({"query": "Explain paid leave"}))

⚠ Troubleshooting
❌ "Only one usage of each socket address"

Ollama already running → do NOT run ollama serve twice.

❌ "Missing some input keys: {'query'}"

Always call:

qa_chain.invoke({"query": "your question"})

❌ FAISS not found

Run:

python scripts/build_index.py

❌ Ollama connection error

Start Ollama:

ollama serve

📦 Requirements (from requirements.txt)
langchain
langchain-community
langchain-core
langchain-text-splitters
langchain-ollama
langchain-huggingface
sentence-transformers
faiss-cpu
pypdf
python-dotenv
Flask

🧪 Example Questions

“Explain paid leave policy.”

“When does earned leave get encashed?”

“What are rules for late attendance?”

“Who approves manpower requisition?”

🤝 Contributing

PRs and suggestions are welcome!

📄 License

MIT License.