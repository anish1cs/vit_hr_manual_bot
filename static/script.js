document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const input = document.getElementById("message-input");
    const chatWindow = document.getElementById("chat-window");
    const historyList = document.getElementById("history-list");
    const newChatBtn = document.getElementById("new-chat-btn");
    const clearAllBtn = document.getElementById("clear-all-history");

    // --- State Management ---
    // We use localStorage so history persists across refreshes
    let allChats = JSON.parse(localStorage.getItem("allChats")) || [];
    let currentChatId = null;

    // Initialize
    init();

    function init() {
        renderHistorySidebar();
        if (allChats.length > 0) {
            // Load the most recent chat
            loadChat(allChats[0].id);
        } else {
            // Start a new chat if none exist
            createNewChat();
        }
    }

    // --- Event Listeners ---

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const message = input.value.trim();
        if (!message) return;

        // 1. Handle "New Chat" state
        // If it's the first message of a new chat, give it a title
        const currentChat = allChats.find(c => c.id === currentChatId);
        if (currentChat && currentChat.messages.length === 1) { // Only welcome msg exists
             // Set title to the first few words of user message
            currentChat.title = message.split(' ').slice(0, 4).join(' ') + "...";
            saveChatsToStorage();
            renderHistorySidebar();
        }

        // 2. Display and save user message
        addMessageToUI(message, "user");
        saveMessageToCurrentChat("user", message);
        input.value = "";

        // 3. Show new typing dots animation
        const loadingElement = addTypingAnimation();

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message }),
            });

            if (!response.ok) throw new Error("Network error");
            const data = await response.json();
            
            // Remove loading animation
            if (loadingElement) loadingElement.remove();

            // Display and save bot message
            addMessageToUI(data.answer, "bot");
            saveMessageToCurrentChat("bot", data.answer);

        } catch (error) {
            console.error("Error:", error);
            if (loadingElement) loadingElement.remove();
            const errorMsg = "Sorry, connection error. Please ensure Ollama is running.";
            addMessageToUI(errorMsg, "bot");
            saveMessageToCurrentChat("bot", errorMsg);
        }
    });

    newChatBtn.addEventListener("click", createNewChat);

    clearAllBtn.addEventListener("click", () => {
        if(confirm("Are you sure you want to delete all chat history?")) {
            localStorage.removeItem("allChats");
            allChats = [];
            createNewChat();
            renderHistorySidebar();
        }
    });


    // --- Helper Functions: Chat Management ---

    function createNewChat() {
        const newId = Date.now().toString();
        const welcomeMsg = { sender: "bot", text: "Hello! How can I help you with the HR policies today?" };
        
        const newSession = {
            id: newId,
            title: "New Chat",
            messages: [welcomeMsg]
        };

        // Add to beginning of array (most recent first)
        allChats.unshift(newSession);
        saveChatsToStorage();
        loadChat(newId);
        renderHistorySidebar();
    }

    function loadChat(id) {
        currentChatId = id;
        const chat = allChats.find(c => c.id === id);
        if (!chat) return;

        chatWindow.innerHTML = ''; // Clear current view
        chat.messages.forEach(msg => {
            addMessageToUI(msg.text, msg.sender);
        });
        renderHistorySidebar(); // To update active state
    }

    function saveMessageToCurrentChat(sender, text) {
        const chat = allChats.find(c => c.id === currentChatId);
        if (chat) {
            chat.messages.push({ sender, text });
            saveChatsToStorage();
        }
    }

    function saveChatsToStorage() {
        localStorage.setItem("allChats", JSON.stringify(allChats));
    }


    // --- Helper Functions: UI Rendering ---

    function renderHistorySidebar() {
        historyList.innerHTML = '';
        allChats.forEach(chat => {
            const li = document.createElement("li");
            li.className = `history-item ${chat.id === currentChatId ? 'active' : ''}`;
            li.textContent = chat.title;
            li.addEventListener("click", () => loadChat(chat.id));
            historyList.appendChild(li);
        });
    }

    function addMessageToUI(text, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${sender}-message`;
        // Use textContent for safety against XSS
        messageDiv.textContent = text; 
        chatWindow.appendChild(messageDiv);
        scrollToBottom();
    }

    // Creates the new 3-dot typing animation structure
    function addTypingAnimation() {
        const messageDiv = document.createElement("div");
        messageDiv.className = "message bot-message loading";
        
        const typingIndicator = document.createElement("div");
        typingIndicator.className = "typing-indicator";
        
        // Create 3 dots
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement("div");
            dot.className = "typing-dot";
            typingIndicator.appendChild(dot);
        }
        
        messageDiv.appendChild(typingIndicator);
        chatWindow.appendChild(messageDiv);
        scrollToBottom();
        return messageDiv;
    }

    function scrollToBottom() {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});