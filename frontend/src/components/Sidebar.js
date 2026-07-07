import React from "react";
import "./Sidebar.css";

function Sidebar({ sessions, activeSession, onSelectSession, onNewChat }) {
  const stats = [
    { label: "Dataset", value: "Olist E-Commerce" },
    { label: "Orders", value: "99,441" },
    { label: "Tables", value: "9" },
    { label: "Region", value: "Brazil" },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">🧞‍♂️</div>
        <span className="sidebar-title">AI-BI Genie</span>
      </div>

      <button className="new-chat-btn" onClick={onNewChat}>
        + New Chat
      </button>

      <div className="sidebar-section">
        <h3 className="section-title">Chat History</h3>
        <div className="history-list">
          {sessions.length === 0 ? (
            <p className="no-history">No conversations yet</p>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={`history-item ${session.id === activeSession ? "active" : ""}`}
                onClick={() => onSelectSession(session.id)}
              >
                <span className="history-icon">💬</span>
                <div className="history-text">
                  <p className="history-title">{session.title}</p>
                  <p className="history-meta">
                    {session.messages.length} message{session.messages.length !== 1 ? "s" : ""}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="sidebar-section">
        <h3 className="section-title">Dataset Info</h3>
        <div className="stats-grid">
          {stats.map((stat, index) => (
            <div key={index} className="stat-card">
              <p className="stat-value">{stat.value}</p>
              <p className="stat-label">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="sidebar-section">
        <h3 className="section-title">Quick Tips</h3>
        <div className="tips-list">
          <div className="tip-item">
            <span className="tip-icon">📊</span>
            <p>Ask about rankings for bar charts</p>
          </div>
          <div className="tip-item">
            <span className="tip-icon">📈</span>
            <p>Ask about trends for line charts</p>
          </div>
          <div className="tip-item">
            <span className="tip-icon">🥧</span>
            <p>Ask about shares for pie charts</p>
          </div>
          
        </div>
      </div>

      
    </div>
  );
}

export default Sidebar;
