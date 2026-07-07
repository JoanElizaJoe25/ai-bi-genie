import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import ChartRenderer from "./ChartRenderer";
import "./MessageBubble.css";

function formatAnswer(text) {
  if (!text) return "";
  let cleaned = text.replace(/\*\*/g, "");
  cleaned = cleaned.replace(/^\* /gm, "• ");
  return cleaned;
}

function MessageBubble({ message }) {
  const [showSQL, setShowSQL] = useState(false);

  if (message.type === "user") {
    return (
      <div className="message-row user-row">
        <div className="message-bubble user-bubble">
          <p>{message.content}</p>
        </div>
        <div className="avatar user-avatar">You</div>
      </div>
    );
  }

  return (
    <div className="message-row bot-row">
      <div className="avatar bot-avatar">🧞</div>
      <div className="message-bubble bot-bubble">
        <div className="bot-content">
          <div className="answer-text">
            <ReactMarkdown
              components={{
                strong: ({ children }) => (
                  <span className="highlight">{children}</span>
                ),
                li: ({ children }) => (
                  <li className="answer-list-item">{children}</li>
                ),
              }}
            >
              {message.content || ""}
            </ReactMarkdown>
          </div>

          {message.chartType && message.chartType !== "none" && message.chartData && message.chartData.labels && (
            <div className="chart-container">
              <ChartRenderer
                chartType={message.chartType}
                chartData={message.chartData}
              />
            </div>
          )}

          {message.sql && (
            <div className="sql-section">
              <button
                className="sql-toggle"
                onClick={() => setShowSQL(!showSQL)}
              >
                {showSQL ? "▼ Hide SQL Query" : "▶ View SQL Query"}
              </button>
              {showSQL && (
                <pre className="sql-code">{message.sql}</pre>
              )}
            </div>
          )}

          {message.error && (
            <p className="error-text">⚠️ {message.error}</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default MessageBubble;

