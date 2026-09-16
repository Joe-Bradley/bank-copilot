const chatForm = document.querySelector("#chat-form");
const messageInput = document.querySelector("#message-input");
const chatMessages = document.querySelector("#chat-messages");
const submitButton = chatForm.querySelector('button[type="submit"]');
const clearHistoryButton = document.querySelector(
    "#clear-history",
);
const savedHistory = localStorage.getItem(
    "bankCopilotHistory",
);
const conversationHistory = savedHistory
    ? JSON.parse(savedHistory)
    : [];
let isSending = false;

function addMessage(role, content) {
    const messageElement = document.createElement("p");
    const label = role === "user"
        ? "你"
        : "AI";

    messageElement.classList.add(
        "message",
        `${role}-message`,
    );
    messageElement.textContent = `${label}：${content}`;
    chatMessages.appendChild(messageElement);
    scrollToLatest();

    return messageElement;
}

function scrollToLatest() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

for (const item of conversationHistory) {
    addMessage(item.role, item.content);
}

clearHistoryButton.addEventListener("click", () => {
    conversationHistory.length = 0;
    localStorage.removeItem("bankCopilotHistory");
    window.location.reload();
});

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (isSending) {
        return;
    }

    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    isSending = true;
    submitButton.disabled = true;

    addMessage("user", message);

    const assistantMessageElement = addMessage(
        "assistant",
        "正在思考……",
    );

    messageInput.value = "";

    try {
        const response = await fetch("/chat/stream", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message: message,
                history: conversationHistory.slice(-10),
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        if (!response.body) {
            throw new Error("响应中没有可读取的内容");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantAnswer = "";

        assistantMessageElement.textContent = "AI：";

        while (true) {
            const { value, done } = await reader.read();

            if (done) {
                break;
            }

            const chunk = decoder.decode(value, {
                stream: true,
            });

            assistantAnswer += chunk;
            assistantMessageElement.textContent += chunk;
            scrollToLatest();
        }

        const finalChunk = decoder.decode();
        assistantAnswer += finalChunk;
        assistantMessageElement.textContent += finalChunk;
        scrollToLatest();

        conversationHistory.push(
            {
                role: "user",
                content: message,
            },
            {
                role: "assistant",
                content: assistantAnswer,
            },
        );

        if (conversationHistory.length > 10) {
            conversationHistory.splice(
                0,
                conversationHistory.length - 10,
            );
        }

        localStorage.setItem(
            "bankCopilotHistory",
            JSON.stringify(conversationHistory),
        );
    } catch (error) {
        assistantMessageElement.textContent = "AI：请求失败，请稍后重试";
        console.error(error);
    } finally {
        isSending = false;
        submitButton.disabled = false;
        messageInput.focus();
    }
});
