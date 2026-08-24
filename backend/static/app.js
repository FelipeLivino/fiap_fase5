const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const messages = document.querySelector("#messages");
const status = document.querySelector("#status");
const newConversationButton = document.querySelector("#new-conversation");

let conversationId = sessionStorage.getItem("cardioia.conversationId");

function appendMessage(author, text, kind) {
  const article = document.createElement("article");
  article.className = `message ${kind}-message`;

  const authorLabel = document.createElement("span");
  authorLabel.className = "message-author";
  authorLabel.textContent = author;

  const paragraph = document.createElement("p");
  paragraph.textContent = text;

  article.append(authorLabel, paragraph);
  messages.append(article);
  messages.scrollTop = messages.scrollHeight;
}

function setLoading(loading) {
  input.disabled = loading;
  sendButton.disabled = loading;
  if (loading) {
    status.textContent = "CardioIA está respondendo…";
  }
}

async function sendMessage(message) {
  status.textContent = "";
  setLoading(true);
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });

    const payload = await response.json();
    if (response.status === 410) {
      conversationId = null;
      sessionStorage.removeItem("cardioia.conversationId");
    }
    if (!response.ok) {
      throw new Error(payload.error?.message || "Não foi possível enviar a mensagem.");
    }

    conversationId = payload.conversation_id;
    sessionStorage.setItem("cardioia.conversationId", conversationId);
    for (const messageItem of payload.messages || []) {
      if (messageItem.type === "text") {
        appendMessage("CardioIA", messageItem.text, "assistant");
      }
    }
    status.textContent = "";
  } catch (error) {
    status.textContent = error.message;
    input.value = message;
  } finally {
    setLoading(false);
    input.focus();
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) {
    status.textContent = "Digite uma mensagem antes de enviar.";
    input.focus();
    return;
  }

  appendMessage("Você", message, "user");
  input.value = "";
  await sendMessage(message);
});

newConversationButton.addEventListener("click", async () => {
  const previousId = conversationId;
  conversationId = null;
  sessionStorage.removeItem("cardioia.conversationId");
  if (previousId) {
    await fetch(`/api/conversations/${encodeURIComponent(previousId)}`, {
      method: "DELETE",
    }).catch(() => undefined);
  }
  messages.replaceChildren();
  appendMessage(
    "CardioIA",
    "Nova conversa iniciada. Use somente informações fictícias.",
    "assistant",
  );
  status.textContent = "";
  input.focus();
});
