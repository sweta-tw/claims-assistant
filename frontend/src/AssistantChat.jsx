
import { useEffect, useRef, useState } from "react";
import { Bot, RotateCcw, Send, UserRound } from "lucide-react";
import { sendChatMessage } from "./api";

const INITIAL_MESSAGE = {
  role: "assistant",
  content:
    "I am your ClaimsIQ assistant. Ask about a claim by ID, for example: What is the status of CLM-1001?",
};

export default function AssistantChat({ token }) {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSubmit(event) {
    event.preventDefault();

    const message = input.trim();
    if (!message || loading) return;

    const history = messages
      .filter((item) => item !== INITIAL_MESSAGE)
      .map(({ role, content }) => ({ role, content }));

    setMessages((current) => [
      ...current,
      { role: "user", content: message },
    ]);
    setInput("");
    setError("");
    setLoading(true);

    try {
      const result = await sendChatMessage(token, message, history);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: result.reply || "The assistant returned an empty response.",
        },
      ]);
    } catch (err) {
      setError(err.message || "Unable to contact the AI assistant.");
    } finally {
      setLoading(false);
    }
  }

  function resetConversation() {
    if (loading) return;
    setMessages([INITIAL_MESSAGE]);
    setInput("");
    setError("");
  }

  return (
    <section className="assistant-chat-page">
      <header className="assistant-chat-header">
        <div className="assistant-chat-heading">
          <div className="assistant-chat-avatar">
            <Bot size={23} />
          </div>
          <div>
            <div className="eyebrow">CLAIMSIQ AI</div>
            <h1>AI Claims Assistant</h1>
            <p>Ask questions about claims using the connected MCP tools.</p>
          </div>
        </div>

        <button
          className="secondary-button"
          onClick={resetConversation}
          disabled={loading}
          type="button"
        >
          <RotateCcw size={15} />
          New chat
        </button>
      </header>

      <div className="assistant-chat-card">
        <div className="assistant-chat-status">
          <span className="online-dot" />
          Authenticated session · Responses may use live claim tools
        </div>

        <div className="assistant-chat-messages" aria-live="polite">
          {messages.map((message, index) => (
            <div
              key={`${index}-${message.role}`}
              className={`chat-message ${
                message.role === "user" ? "chat-message-user" : "chat-message-assistant"
              }`}
            >
              <div className="chat-message-avatar">
                {message.role === "user" ? (
                  <UserRound size={16} />
                ) : (
                  <Bot size={16} />
                )}
              </div>
              <div className="chat-message-content">
                <div className="chat-message-role">
                  {message.role === "user" ? "You" : "ClaimsIQ Assistant"}
                </div>
                <div className="chat-message-text">{message.content}</div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="chat-message chat-message-assistant">
              <div className="chat-message-avatar">
                <Bot size={16} />
              </div>
              <div className="chat-message-content">
                <div className="chat-message-role">ClaimsIQ Assistant</div>
                <div className="chat-typing">Thinking and checking available tools...</div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {error && (
          <div className="chat-error" role="alert">
            {error}
          </div>
        )}

        <form className="assistant-chat-composer" onSubmit={handleSubmit}>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                handleSubmit(event);
              }
            }}
            placeholder="Ask about a claim, its status, or a supported operation..."
            aria-label="Message the AI assistant"
            rows={2}
            maxLength={4000}
            disabled={loading}
          />
          <button
            className="primary-button chat-send-button"
            type="submit"
            disabled={loading || !input.trim()}
            aria-label="Send message"
          >
            <Send size={16} />
            Send
          </button>
        </form>

        <div className="assistant-chat-disclaimer">
          Verify consequential claim changes against the claims system. The assistant can only
          perform operations exposed by the backend's MCP tools and authorized for your role.
        </div>
      </div>
    </section>
  );
}
