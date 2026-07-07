import React, { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import InputBar from "./InputBar";
import "./ChatWindow.css";

function ChatWindow({ sessionId, onNewMessage }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, statusText]);

  useEffect(() => {
    setMessages([]);
  }, [sessionId]);

  const sendMessage = async (question) => {
    if (!question.trim()) return;

    const userMessage = { type: "user", content: question };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setStatusText("Starting...");

    try {
      const response = await fetch("http://127.0.0.1:8000/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: question,
          session_id: sessionId,
        }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = "";
      let finalData = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        let currentEvent = null;

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            currentEvent = line.substring(7).trim();
          } else if (line.startsWith("data: ") && currentEvent) {
            try {
              const data = JSON.parse(line.substring(6));

              if (currentEvent === "status") {
                setStatusText(data.message);
              } else if (currentEvent === "error") {
                const errorMsg = {
                  type: "bot",
                  content: data.message,
                  error: data.detail || data.message,
                  sql: data.sql || "",
                };
                setMessages((prev) => [...prev, errorMsg]);
                setLoading(false);
                setStatusText("");
                return;
              } else if (currentEvent === "complete") {
                finalData = data;
              }
            } catch (e) {
              // skip parse errors
            }
            currentEvent = null;
          }
        }
      }

      if (finalData) {
        const botMessage = {
          type: "bot",
          content: finalData.answer,
          sql: finalData.sql_query,
          chartType: finalData.chart_type,
          chartData: finalData.chart_data,
          error: finalData.error,
        };
        setMessages((prev) => [...prev, botMessage]);
        onNewMessage(question, finalData.answer);
      }
    } catch (error) {
      const errorMessage = {
        type: "bot",
        content: "Sorry, something went wrong. Please try again.",
        error: error.message,
      };
      setMessages((prev) => [...prev, errorMessage]);
    }

    setLoading(false);
    setStatusText("");
  };

  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <div className="welcome-icon">🧞‍♂️</div>
            <h2>What would you like to know?</h2>
            <p>Ask me anything about the Brazilian e-commerce dataset</p>
            <div className="suggestions">
              <button onClick={() => sendMessage("How many total orders are there?")}>
                📦 Total orders count
              </button>
              <button onClick={() => sendMessage("What are the top 5 product categories by revenue?")}>
                🏆 Top 5 categories by revenue
              </button>
              <button onClick={() => sendMessage("Show me orders per month in 2017")}>
                📈 Monthly orders trend 2017
              </button>
              <button onClick={() => sendMessage("What is the distribution of payment types?")}>
                💳 Payment type distribution
              </button>
            </div>
          </div>
        )}

        {messages.map((msg, index) => (
          <MessageBubble key={index} message={msg} />
        ))}

        {loading && (
          <div className="loading-bubble">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <p className="status-text">{statusText}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <InputBar onSend={sendMessage} disabled={loading} />
    </div>
  );
}

export default ChatWindow;


