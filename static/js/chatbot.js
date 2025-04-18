class AIQuizChatbot {
    constructor() {
        this.chatContainer = null;
        this.messageList = null;
        this.context = {};
        this.suggestions = [
            "help",
            "quiz rules",
            "my progress",
            "upcoming quizzes",
            "technical issues",
            "study tips"
        ];
        this.init();
    }

    init() {
        this.createChatbotUI();
        this.initEventListeners();
        this.addWelcomeMessage();
    }

    createChatbotUI() {
        const chatbot = document.createElement('div');
        chatbot.className = 'chatbot-container';
        chatbot.innerHTML = `
            <div class="chatbot-toggle">
                <i class="fas fa-comments"></i>
            </div>
            <div class="chatbot-box">
                <div class="chatbot-header">
                    <h3>AI Quiz Assistant</h3>
                    <div class="chatbot-controls">
                        <button class="clear-btn" title="Clear chat"><i class="fas fa-trash"></i></button>
                        <button class="minimize-btn">−</button>
                    </div>
                </div>
                <div class="chatbot-messages"></div>
                <div class="chatbot-suggestions"></div>
                <div class="chatbot-input">
                    <input type="text" placeholder="Ask me anything...">
                    <button type="submit">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(chatbot);
        this.chatContainer = chatbot;
        this.messageList = chatbot.querySelector('.chatbot-messages');
        this.suggestionsContainer = chatbot.querySelector('.chatbot-suggestions');
    }

    initEventListeners() {
        const toggle = this.chatContainer.querySelector('.chatbot-toggle');
        const minimizeBtn = this.chatContainer.querySelector('.minimize-btn');
        const clearBtn = this.chatContainer.querySelector('.clear-btn');
        const input = this.chatContainer.querySelector('input');
        const sendBtn = this.chatContainer.querySelector('button[type="submit"]');

        toggle.addEventListener('click', () => this.toggleChat());
        minimizeBtn.addEventListener('click', () => this.toggleChat());
        clearBtn.addEventListener('click', () => this.clearChat());
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && input.value.trim()) {
                this.handleUserMessage(input.value);
                input.value = '';
            }
        });

        input.addEventListener('input', () => {
            this.updateSuggestions(input.value);
        });

        sendBtn.addEventListener('click', () => {
            if (input.value.trim()) {
                this.handleUserMessage(input.value);
                input.value = '';
            }
        });
    }

    addWelcomeMessage() {
        const welcomeMessage = `Hello! 👋 I'm your AI Quiz Assistant. I can help you with:
• Quiz information and rules
• Course details and progress
• Technical support
• Study tips and guidance
• And much more!

Type 'help' to see all available options or ask me anything!`;
        
        this.addMessage('bot', welcomeMessage);
        this.showSuggestions();
    }

    updateSuggestions(input) {
        if (!input.trim()) {
            this.showSuggestions();
            return;
        }

        const matchingSuggestions = this.suggestions.filter(suggestion =>
            suggestion.toLowerCase().includes(input.toLowerCase())
        );

        this.renderSuggestions(matchingSuggestions);
    }

    showSuggestions() {
        this.renderSuggestions(this.suggestions);
    }

    renderSuggestions(suggestions) {
        this.suggestionsContainer.innerHTML = suggestions
            .map(suggestion => `
                <button class="suggestion-btn" onclick="this.closest('.chatbot-container').querySelector('input').value='${suggestion}'">
                    ${suggestion}
                </button>
            `)
            .join('');
    }

    toggleChat() {
        this.chatContainer.classList.toggle('chatbot-open');
        if (this.chatContainer.classList.contains('chatbot-open')) {
            this.chatContainer.querySelector('input').focus();
        }
    }

    clearChat() {
        this.messageList.innerHTML = '';
        this.addWelcomeMessage();
    }

    async handleUserMessage(message) {
        if (!message.trim()) return;

        // Add user message to chat
        this.addMessage('user', message);

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await this.getBotResponse(message);
            // Remove typing indicator and add bot response
            this.removeTypingIndicator();
            this.addMessage('bot', response);
            
            // Show suggestions after bot response
            this.showSuggestions();
        } catch (error) {
            this.removeTypingIndicator();
            this.addMessage('bot', 'Sorry, I encountered an error. Please try again.');
        }
    }

    addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        // Format message content if it contains lists
        const formattedContent = this.formatMessage(content);
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${formattedContent}
            </div>
        `;
        
        this.messageList.appendChild(messageDiv);
        this.messageList.scrollTop = this.messageList.scrollHeight;
    }

    formatMessage(content) {
        // Convert bullet points
        content = content.replace(/•/g, '&bull;');
        
        // Convert numbered lists
        content = content.replace(/^\d+\./gm, (match) => `<strong>${match}</strong>`);
        
        // Convert newlines to <br>
        content = content.replace(/\n/g, '<br>');
        
        return content;
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        this.messageList.appendChild(typingDiv);
        this.messageList.scrollTop = this.messageList.scrollHeight;
    }

    removeTypingIndicator() {
        const typingIndicator = this.messageList.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    async getBotResponse(message) {
        try {
            const response = await fetch('/chatbot/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    }

    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize chatbot when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AIQuizChatbot();
});
