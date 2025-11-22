# scripts/start_chat.py

from langchain_core.messages import HumanMessage, AIMessage
# --- Import both of our logic functions ---
from logic.conversational_logic import create_conversational_chain
from logic.multi_query_logic import create_multi_query_chain

def run_conversational_bot(rag_chain):
    """Handles the chat loop for the bot with memory."""
    chat_history = []
    print("\n✅ Conversational Bot ready! It now has memory. Type 'exit' to quit.")
    while True:
        query = input("\nAsk a follow-up question: ")
        if query.lower() in ["exit", "quit"]:
            break
        
        result = rag_chain.invoke({"input": query, "chat_history": chat_history})
        print("\nAnswer:", result['answer'])
        
        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=result['answer']))

def run_multi_query_bot(qa_chain):
    """Handles the chat loop for the bot without memory."""
    print("\n✅ Multi-Query Bot ready! It will generate sub-questions. Type 'exit' to quit.")
    while True:
        query = input("\nAsk a complex or broad policy question: ")
        if query.lower() in ["exit", "quit"]:
            break
        
        result = qa_chain.invoke(query)
        print("\nAnswer:", result['result'])

def main():
    print("=== HR POLICY CHATBOT (Terminal) ===")
    
    while True:
        print("\nPlease choose a bot to start:")
        print("1: Conversational Bot (with chat memory)")
        print("2: Advanced Multi-Query Bot (for broad questions)")
        choice = input("Enter your choice (1 or 2, or 'exit' to quit): ")

        if choice == '1':
            rag_chain = create_conversational_chain()
            run_conversational_bot(rag_chain)
            break
        elif choice == '2':
            qa_chain = create_multi_query_chain()
            run_multi_query_bot(qa_chain)
            break
        elif choice.lower() in ["exit", "quit"]:
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()