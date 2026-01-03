document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const launcherBtn = document.getElementById('launcher-btn');
    const chatWidget = document.getElementById('chat-widget');
    const minimizeBtn = document.getElementById('minimize-btn');
    const chatArea = document.getElementById('chat-area');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const typingIndicator = document.getElementById('typing-indicator');
    const quickActions = document.querySelector('.quick-actions'); // For delegation

    let isOpen = false;

    // Toggle Chat Widget
    function toggleChat() {
        isOpen = !isOpen;
        if (isOpen) {
            chatWidget.classList.add('active');
            launcherBtn.style.transform = 'scale(0) rotate(180deg)';
            setTimeout(() => userInput.focus(), 300); // Focus input on open
        } else {
            chatWidget.classList.remove('active');
            launcherBtn.style.transform = 'scale(1) rotate(0deg)';
        }
    }

    launcherBtn.addEventListener('click', toggleChat);
    minimizeBtn.addEventListener('click', toggleChat);

    // Quick Actions Click Handler
    quickActions.addEventListener('click', (e) => {
        if (e.target.classList.contains('chip')) {
            const query = e.target.getAttribute('data-query');
            userInput.value = query;
            sendMessage();
        }
    });

    // Enter to Send
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    // Click to Send
    sendBtn.addEventListener('click', sendMessage);

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // Clear input
        userInput.value = '';

        // Add User Message
        addMessage(text, 'user');

        // Show Typing
        showTyping(true);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();

            // Remove Typing
            showTyping(false);

            if (data.error) {
                addMessage(`⚠️ Error: ${data.error}`, 'bot');
            } else {
                addMessage(data.answer, 'bot', data);
            }

        } catch (error) {
            showTyping(false);
            addMessage('❌ Error connecting to server. Please try again.', 'bot');
            console.error(error);
        }
    }

    function addMessage(text, type, data = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${type}`;

        // Parse Markdown
        let htmlContent = marked.parse(text);

        // Style citations [1], [2] etc. (and handle "[1 from search]" format)
        htmlContent = htmlContent.replace(/\[(\d+)(?: from search)?\]/g, '<span class="citation-link">[$1]</span>');

        let html = `
            <div class="bubble">
                ${htmlContent}
            </div>
            <div class="message-meta">
                ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
        `;

        if (data && data.escalation) {
            html += `
                <div class="escalation-box" style="margin-top:8px; padding:12px; background:#fff1f2; border:1px solid #fda4af; border-radius:8px;">
                    <div style="color:#e11d48; font-weight:600; margin-bottom:4px;">
                        <i class="fas fa-headset"></i> Human Agent Needed?
                    </div>
                    <p style="font-size:12px; color:#9f1239; margin-bottom:8px;">
                        This query seems complex. Would you like to connect with a specialist?
                    </p>
                    <button class="escalate-btn" data-action="connect-agent" style="background:#e11d48; color:white; border:none; padding:6px 12px; border-radius:12px; font-size:12px; cursor:pointer;">
                        Connect Now
                    </button>
                </div>
            `;
        }

        // Sources (if debug needed, or user wants to see citations)
        // Sources Display
        if (data && data.sources && data.sources.length > 0) {
            html += `<div class="sources-container" style="margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(0,0,0,0.05);">
                <div style="font-size: 11px; color: #6b7280; font-weight: 600; margin-bottom: 4px;">📚 Sources:</div>
                <div style="display: flex; flex-wrap: wrap; gap: 4px;">`;

            data.sources.forEach((source, index) => {
                // simple cleanup of source_id to be more readable
                // e.g. "manual.txt::row_5" -> "manual.txt"
                let label = source.source_id.split('::')[0];
                html += `
                    <div class="source-chip" title="${label}" style="
                        background: rgba(0,0,0,0.04); 
                        border: 1px solid rgba(0,0,0,0.05);
                        border-radius: 4px;
                        padding: 2px 6px;
                        font-size: 10px;
                        color: #4b5563;
                        display: flex;
                        align-items: center;
                        gap: 4px;
                    ">
                        <span style="font-weight: 600; color: #2563eb;">[${index + 1}]</span>
                        <span style="max-width: 100px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${label}</span>
                    </div>
                `;
            });

            html += `</div></div>`;
        }

        msgDiv.innerHTML = html;
        chatArea.insertBefore(msgDiv, typingIndicator); // Insert before typing indicator

        // Move typing indicator to bottom
        chatArea.appendChild(typingIndicator);

        scrollToBottom();
    }

    // Agent Escalation Simulation
    chatArea.addEventListener('click', (e) => {
        const btn = e.target.closest('.escalate-btn');
        if (btn && btn.dataset.action === 'connect-agent') {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';
            setTimeout(() => {
                const agent = ['Sarah', 'Mike', 'Priya'][Math.floor(Math.random() * 3)];
                const agentMsg = document.createElement('div');
                agentMsg.className = 'message bot';
                agentMsg.innerHTML = `
                    <div class="bubble" style="background: linear-gradient(135deg, #10b981, #059669); color:white;">
                        <strong>💁‍♀️ Agent ${agent} joined the chat</strong><br>
                        Hi there! I'm reading through your issue now. Give me a moment.
                    </div>
                    <div class="message-meta">Agent • Just now</div>
                `;
                chatArea.insertBefore(agentMsg, typingIndicator);
                scrollToBottom();
                btn.innerHTML = 'Connected';
                btn.style.background = '#22c55e';
            }, 2000);
        }
    });

    function showTyping(show) {
        typingIndicator.style.display = show ? 'flex' : 'none';
        scrollToBottom();
    }

    function scrollToBottom() {
        chatArea.scrollTop = chatArea.scrollHeight;
    }
});
