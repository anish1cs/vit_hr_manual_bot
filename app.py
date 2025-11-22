# app.py

from flask import Flask, request, jsonify, render_template
from scripts.logic.conversational_logic import load_local_chain_with_guardrails

app = Flask(__name__)
app.secret_key = "super_secret_key"

# -----------------------------
# CONFIGURATION
# -----------------------------
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_DB_PATH = "data/vector_store"
LLM_MODEL_NAME = "gemma:2b"
DEBUG_RETRIEVAL = True

qa_chain = None


# -----------------------------------------------------
# LOAD RAG CHAIN ONCE BEFORE FIRST REQUEST
# -----------------------------------------------------
@app.before_request
def load_rag_chain():
    global qa_chain
    if qa_chain is None:
        print("\n🚀 Starting Flask HR Policy Chatbot — Ollama + FAISS + Gemma:2b\n")
        print("🔧 Initializing Local RAG Chain (Ollama + FAISS)...")

        qa_chain = load_local_chain_with_guardrails(
            llm_model_name=LLM_MODEL_NAME,
            embedding_model_name=EMBEDDING_MODEL_NAME,
            vector_db_path=VECTOR_DB_PATH,
            debug_retrieval=DEBUG_RETRIEVAL,
        )

        print("\n✅ RAG chain loaded successfully.")
        print("CHAIN IS READY.")
        print("INPUT KEYS:", qa_chain.input_keys)
        print("OUTPUT KEYS:", qa_chain.output_keys)
        print("--------------------------------------")


# -----------------------------
# FRONTEND ROUTE
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------------------------------
# CHAT ENDPOINT — USES `query` AS CHAIN INPUT
# -----------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    global qa_chain

    if qa_chain is None:
        return jsonify({"answer": "Chatbot failed to initialize."}), 500

    user_message = request.json.get("message", "").strip()

    if not user_message:
        return jsonify({"answer": "Please type a message."}), 400

    # DEBUG
    print("\n🔥 CHAT ENDPOINT CALLED:")
    print("CHAIN INPUT KEYS =", qa_chain.input_keys)
    print("CHAIN OUTPUT KEYS =", qa_chain.output_keys)
    print(f"[📥 USER] {user_message}")

    try:
        # Outer chain input key is "query"
        result = qa_chain.invoke({"query": user_message})

        print("\n[📤 RAW OUTPUT]", result)

        bot_answer = result.get("result", "Sorry, I couldn't process your request.")

        return jsonify({"answer": bot_answer})

    except Exception as e:
        print("❌ Chat Error:", e)

        if "ollama" in str(e).lower():
            return jsonify(
                {"answer": "Sorry, connection error. Please ensure Ollama is running."}
            )

        return jsonify({"answer": "Sorry, an unexpected error occurred."}), 500


# -----------------------------
# MAIN ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
