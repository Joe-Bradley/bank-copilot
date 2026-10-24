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

//去浏览器里面的localStorage里面取出bankCopilotHistory的值，如果有值就解析成数组，如果没有值就初始化为空数组
const conversationHistory = savedHistory
    ? JSON.parse(savedHistory)
    : [];
let isSending = false;

/**
 * 添加消息到聊天窗口
 * @param {string} role - 消息的角色，
 * "user"表示用户，"assistant"表示AI助手
 * @param {string} content - 消息的内容
 * @returns {HTMLElement} - 创建的消息元素
 */
function addMessage(role, content) {
    const messageElement = document.createElement("p");
    const label = role === "user"
        ? "你"
        : "AI";

    // 为消息元素添加CSS类，可能是"user-message"或"assistant-message"，用于不同的样式
    messageElement.classList.add(
        "message",
        `${role}-message`,
    );

    // 设置消息元素的文本内容
    messageElement.textContent = `${label}：${content}`;

    // 将消息元素添加到聊天消息容器中
    chatMessages.appendChild(messageElement);

    // 滚动聊天窗口到最新消息
    scrollToLatest();

    return messageElement;
}

/**
 * 滚动聊天窗口到最新消息
*/
function scrollToLatest() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * 初始化聊天窗口，加载历史消息
 */
for (const item of conversationHistory) {
    addMessage(item.role, item.content);
}

/**
 * 清除聊天历史记录
 */
clearHistoryButton.addEventListener("click", () => {
    conversationHistory.length = 0;
    localStorage.removeItem("bankCopilotHistory");
    window.location.reload();
});

/**
 * 处理聊天表单提交事件
 */

//event就是submit事件对象
//async就是异步函数
chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    // 如果正在发送消息，则直接返回，避免重复发送
    if (isSending) {
        return;
    }

    // 获取用户输入的消息，并去掉首尾空格
    const message = messageInput.value.trim();

    // 如果消息为空，则直接返回，避免发送空消息
    if (!message) {
        return;
    }

    // 设置发送状态，禁用提交按钮，防止重复发送
    isSending = true;
    submitButton.disabled = true;

    // 将用户消息添加到聊天窗口
    addMessage("user", message);

    // 将AI助手的消息添加到聊天窗口，初始内容为"正在思考……"
    const assistantMessageElement = addMessage(
        "assistant",
        "正在思考……",
    );

    // 清空输入框
    messageInput.value = "";


    // 发送消息到服务器，并处理响应
    try {
        // 发送POST请求到服务器的/chat/stream接口，传递用户消息和历史对话
        const response = await fetch("/chat/stream", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            // 将用户消息和历史对话转换为JSON字符串作为请求体发送
            body: JSON.stringify({
                message: message,
                // 只保留最近10条历史对话，避免请求体过大
                history: conversationHistory.slice(-10),
            }),
        });

        // 如果响应状态码不是200，则抛出错误
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        // 如果响应体为空，则抛出错误
        if (!response.body) {
            throw new Error("响应中没有可读取的内容");
        }

        // 获取响应体的可读流，并创建文本解码器
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        // 初始化AI助手的回答内容为空字符串
        let assistantAnswer = "";

        // 将AI助手的消息元素的文本内容设置为"AI："
        assistantMessageElement.textContent = "AI：";

        // 循环读取响应体的流，直到读取完毕
        while (true) {

            // 请求读取一块数据，如果读取完毕，则done为true，否则为false
            const { value, done } = await reader.read();

            // 如果读取完毕，则跳出循环
            if (done) {
                break;
            }

            // 将读取到的数据解码为字符串
            const chunk = decoder.decode(value, {
                stream: true,
            });

            // 将读取到的数据追加到AI助手的回答内容和消息元素中
            assistantAnswer += chunk;
            assistantMessageElement.textContent += chunk;
            scrollToLatest();
        }

        // 读取完毕后，解码最后一块数据，并追加到AI助手的回答内容和消息元素中
        const finalChunk = decoder.decode();
        assistantAnswer += finalChunk;
        assistantMessageElement.textContent += finalChunk;
        scrollToLatest();

        // 将用户消息和AI助手的回答添加到历史对话中
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

        // 如果历史对话超过10条，则删除最早的对话，保持最近10条
        if (conversationHistory.length > 10) {
            conversationHistory.splice(
                0,
                conversationHistory.length - 10,
            );
        }

        // 将历史对话保存到浏览器的localStorage中，键名为"bankCopilotHistory"，值为JSON字符串
        localStorage.setItem(
            "bankCopilotHistory",
            JSON.stringify(conversationHistory),
        );
    } catch (error) {
        // 如果请求失败，则将AI助手的消息元素的文本内容设置为"AI：请求失败，请稍后重试"，并在控制台输出错误信息
        assistantMessageElement.textContent = "AI：请求失败，请稍后重试";
        console.error(error);
    } finally {
        // 无论请求成功还是失败，都将发送状态重置为false，启用提交按钮，并将输入框聚焦
        isSending = false;
        submitButton.disabled = false;
        messageInput.focus();
    }
});
