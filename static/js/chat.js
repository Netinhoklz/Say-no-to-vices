document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.querySelector('.chat-container');
    if (!chatContainer) return;

    const conversationId = chatContainer.dataset.conversationId;
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const messageList = document.getElementById('message-list');
    const clearChatBtn = document.getElementById('clear-chat-btn');

    const TYPING_DELAY = 5000;
    let messageQueue = [];
    let typingTimeout = null;

    /**
     * Envia as mensagens agrupadas da fila para o backend.
     */
    const sendGroupedMessages = async () => {
        if (messageQueue.length === 0) return;

        const combinedMessage = messageQueue.join('\n');
        messageQueue = [];

        toggleTypingIndicator(true);

        try {
            const response = await fetch(`/send_message/${conversationId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: combinedMessage,
                    client_timestamp: new Date().toISOString()
                }),
            });

            if (!response.ok) throw new Error(`Erro do servidor: ${response.statusText}`);

            const data = await response.json();
            const parsedReply = marked.parse(data.reply);
            addMessage(parsedReply, 'bot', true);

        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            addMessage('Ocorreu um erro de comunicação. Por favor, tente novamente.', 'bot');
        } finally {
            toggleTypingIndicator(false);
        }
    };

    chatForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const userMessage = messageInput.value.trim();
        if (!userMessage) return;

        addMessage(userMessage, 'user');
        messageQueue.push(userMessage);
        messageInput.value = '';
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(sendGroupedMessages, TYPING_DELAY);
    });

    clearChatBtn.addEventListener('click', async () => {
        const confirmation = confirm(
            "ATENÇÃO!\n\nIsso apagará permanentemente toda a sua conversa e seus dados iniciais.\n\nVocê será redirecionado para a tela inicial para recomeçar. Deseja continuar?"
        );
        if (confirmation) {
            try {
                const response = await fetch(`/clear_chat/${conversationId}`, { method: 'POST' });
                if (response.ok) {
                    window.location.href = '/';
                } else {
                    alert('Falha ao apagar o histórico no servidor.');
                }
            } catch (error) {
                console.error('Erro ao limpar o chat:', error);
                alert('Ocorreu um erro de comunicação.');
            }
        }
    });

    const addMessage = (content, type, isHtml = false) => {
        const messageContainer = document.createElement('div');
        messageContainer.className = `message ${type}-message`;
        const messageContentDiv = document.createElement('div');
        messageContentDiv.className = 'message-content';
        if (isHtml) {
            messageContentDiv.innerHTML = content;
        } else {
            messageContentDiv.textContent = content;
        }
        messageContainer.appendChild(messageContentDiv);
        messageList.appendChild(messageContainer);
        scrollToBottom();
        if (isHtml) {
            messageContentDiv.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
        }
    };

    const toggleTypingIndicator = (show) => {
        let indicator = document.getElementById('typing-indicator');
        if (show) {
            if (!indicator) {
                indicator = document.createElement('div');
                indicator.id = 'typing-indicator';
                indicator.className = 'message bot-message typing-indicator';
                indicator.innerHTML = `<span></span><span></span><span></span>`;
                messageList.appendChild(indicator);
                scrollToBottom();
            }
        } else if (indicator) {
            indicator.remove();
        }
    };

    const scrollToBottom = () => {
        messageList.scrollTop = messageList.scrollHeight;
    };

    document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
    scrollToBottom();
});