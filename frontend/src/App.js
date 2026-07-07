import React, { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import Sidebar from "./components/Sidebar";
import "./App.css";

function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState("session_" + Date.now());

  const addToHistory = (question, answer) => {
    setSessions((prev) => {
      const existing = prev.find((s) => s.id === activeSession);
      if (existing) {
        return prev.map((s) =>
          s.id === activeSession
            ? { ...s, messages: [...s.messages, { question, answer }] }
            : s
        );
      }
      return [
        ...prev,
        {
          id: activeSession,
          title: question.length > 35 ? question.substring(0, 35) + "..." : question,
          messages: [{ question, answer }],
          timestamp: new Date(),
        },
      ];
    });
  };

  const startNewChat = () => {
    setActiveSession("session_" + Date.now());
  };

  return (
    <div className="app">
      <Sidebar
        sessions={sessions}
        activeSession={activeSession}
        onSelectSession={setActiveSession}
        onNewChat={startNewChat}
      />
      <div className="main-area">
        <header className="app-header">
          <h1>🧞‍♂️ AI-BI Genie</h1>
          <p>Conversational analytics on e-commerce data</p>
        </header>
        <ChatWindow
          sessionId={activeSession}
          onNewMessage={addToHistory}
        />
      </div>
    </div>
  );
}

export default App;



