import React, { useState, useRef, useEffect } from "react";

export default function SpanishTeacherChat() {
  const [input, setInput] = useState("");
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const conversationEndRef = useRef(null);

  const handleSend = async () => {
    if (!input.trim()) return;
    setLoading(true);

    // Add user message to conversation
    const newConversation = [
      ...conversation,
      { role: "user", content: input }
    ];
    setConversation(newConversation);

    try {
      // Call your backend API
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
      });
      const data = await response.json();

      // Add AI response to conversation
      setConversation([
        ...newConversation,
        { role: "assistant", content: data.reply }
      ]);
      setInput("");
    } catch (error) {
      alert("Error communicating with backend");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (conversationEndRef.current) {
      conversationEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [conversation, loading]);

  return (
    <div
      style={{
        height: "100vh",
        width: "100vw",
        display: "flex",
        flexDirection: "column",
        background: "#f7f7f7"
      }}
    >
      <h2 style={{ textAlign: "center", margin: "16px 0 0 0" }}>Spanish Teacher Chat</h2>
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          margin: "16px auto 0 auto",
          width: "100%",
          maxWidth: 800,
          background: "#fff",
          border: "1px solid #ccc",
          borderRadius: 8,
          padding: 24,
          boxSizing: "border-box",
          display: "flex",
          flexDirection: "column"
        }}
      >
        {conversation.map((msg, idx) => (
          <div
            key={idx}
            style={{
              margin: "8px 0",
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              background: msg.role === "user" ? "#e6f7ff" : "#f0f0f0",
              padding: "10px 16px",
              borderRadius: 16,
              maxWidth: "80%",
              wordBreak: "break-word"
            }}
          >
            <b style={{ color: msg.role === "user" ? "#1890ff" : "#888" }}>
              {msg.role === "user" ? "You" : "AI"}:
            </b>{" "}{msg.content}
          </div>
        ))}
        {loading && <div><i>AI is typing...</i></div>}
        <div ref={conversationEndRef} />
      </div>
      <div
        style={{
          width: "100%",
          maxWidth: 800,
          margin: "0 auto",
          display: "flex",
          alignItems: "center",
          padding: 16,
          background: "#fff",
          borderTop: "1px solid #ccc"
        }}
      >
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === "Enter") handleSend(); }}
          style={{
            flex: 1,
            padding: 12,
            fontSize: 16,
            borderRadius: 8,
            border: "1px solid #ccc",
            marginRight: 8
          }}
          disabled={loading}
          placeholder="Type your message in Spanish..."
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          style={{
            padding: "12px 24px",
            fontSize: 16,
            borderRadius: 8,
            background: "#1890ff",
            color: "#fff",
            border: "none",
            cursor: loading || !input.trim() ? "not-allowed" : "pointer"
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}

