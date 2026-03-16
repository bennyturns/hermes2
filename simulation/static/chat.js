// ─── Agent Brainstorm Chat ───

function toggleChat() {
    const panel = document.getElementById('chat-panel');
    const toggle = document.getElementById('chat-toggle');
    const icon = document.getElementById('chat-icon');
    panel.classList.toggle('open');
    toggle.classList.toggle('open');
    icon.innerHTML = panel.classList.contains('open') ? '&#10005;' : '{AI}';
    if (panel.classList.contains('open')) {
        document.getElementById('chat-input').focus();
    }
}

function switchChatContext(ctx) {
    // Update the global context used by the page
    if (typeof CHAT_CONTEXT !== 'undefined') {
        // Can't reassign const, but the select reflects the user's choice
    }
}

function getChatContext() {
    const select = document.getElementById('chat-context-select');
    if (select) return select.value;
    if (typeof CHAT_CONTEXT !== 'undefined') return CHAT_CONTEXT;
    return 'blueprint';
}

function sendChat() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    // Add user message
    addChatMessage('user', msg);
    input.value = '';

    // Show typing indicator
    const typing = document.getElementById('chat-typing');
    typing.classList.add('active');
    scrollChat();

    // Collect field values if the page provides a collectFieldValues function
    let fields = {};
    if (typeof collectFieldValues === 'function') {
        fields = collectFieldValues();
    }

    // Call backend
    fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ message: msg, context: getChatContext(), fields: fields })
    })
    .then(r => r.json())
    .then(data => {
        // Simulate thinking delay (800-1800ms) for realism
        const delay = 800 + Math.random() * 1000;
        setTimeout(() => {
            typing.classList.remove('active');
            addChatMessage('agent', data.response);
            // Apply any field updates from the agent
            if (data.field_updates && typeof applyFieldUpdates === 'function') {
                applyFieldUpdates(data.field_updates);
                addChatMessage('agent', '(Fields updated — check the highlighted values above.)');
            }
        }, delay);
    })
    .catch(() => {
        typing.classList.remove('active');
        addChatMessage('agent', 'Sorry, I encountered an error. Please try again.');
    });
}

function addChatMessage(role, text) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = 'chat-msg ' + role;
    div.innerHTML = `
        <div>
            <div class="chat-msg-label">${role === 'user' ? 'You' : 'Agent'}</div>
            <div class="chat-msg-bubble">${escapeHtml(text)}</div>
        </div>
    `;
    container.appendChild(div);
    scrollChat();
}

function scrollChat() {
    const container = document.getElementById('chat-messages');
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Set the context dropdown to match the page context on load
document.addEventListener('DOMContentLoaded', function() {
    const select = document.getElementById('chat-context-select');
    if (select && typeof CHAT_CONTEXT !== 'undefined') {
        select.value = CHAT_CONTEXT;
    }
});
