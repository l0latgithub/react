import React, { useState, useEffect, useRef } from 'react';
import './ChatbotInterface.css';

const ChatbotInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [showWelcome, setShowWelcome] = useState(true);
  const messagesEndRef = useRef(null);

  const capabilities = [
    "Natural language understanding and generation",
    "Contextual conversation memory",
    "Knowledge across multiple domains",
    "Code generation and explanation",
    "Text summarization and analysis",
    "Creative writing and brainstorming"
  ];

  const limitations = [
    "Cannot browse the internet in real-time",
    "May occasionally generate incorrect information",
    "Limited knowledge of events after October 2023",
    "Cannot perform physical actions",
    "No voice interaction capability",
    "Cannot process images or videos"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (inputValue.trim() === '') return;

    const userMessage = { text: inputValue, sender: 'user' };
    setMessages([...messages, userMessage]);
    setInputValue('');
    setShowWelcome(false);

    // Simulate bot response
    setTimeout(() => {
      const botMessage = { text: "I'm processing your request. This is a simulated response in the demo interface.", sender: 'bot' };
      setMessages(prev => [...prev, botMessage]);
    }, 1000);
  };

  const handleSuggestionClick = (suggestion) => {
    const userMessage = { text: suggestion, sender: 'user' };
    setMessages([...messages, userMessage]);
    setShowWelcome(false);

    // Simulate bot response to suggestion
    setTimeout(() => {
      const botMessage = { text: `You asked about "${suggestion}". This is a simulated response in the demo interface.`, sender: 'bot' };
      setMessages(prev => [...prev, botMessage]);
    }, 1000);
  };

  const suggestions = [
    "What can you do?",
    "How does this work?",
    "Explain AI to me",
    "Tell me a joke"
  ];

  return (
    <div className="chatbot-container">
      {showWelcome && (
        <div className="welcome-screen">
          <h1>Welcome to SmartBot</h1>
          <p>Your intelligent assistant for information, creativity, and productivity</p>
          
          <div className="welcome-cards">
            <div className="welcome-card">
              <h2>Start Conversation</h2>
              <p>Discover what I can do for you:</p>
              <ul>
                {capabilities.map((cap, index) => (
                  <li key={index}>{cap}</li>
                ))}
              </ul>
              <button 
                className="card-button"
                onClick={() => handleSuggestionClick("What can you do?")}
              >
                Ask About Capabilities
              </button>
            </div>
            
            <div className="welcome-card">
              <h2>What I Can't Do Yet</h2>
              <p>Current limitations to be aware of:</p>
              <ul>
                {limitations.map((limit, index) => (
                  <li key={index}>{limit}</li>
                ))}
              </ul>
              <button 
                className="card-button"
                onClick={() => handleSuggestionClick("What are your limitations?")}
              >
                Ask About Limitations
              </button>
            </div>
          </div>
        </div>
      )}
      
      <div className="chat-window">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            {message.text}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      {messages.length === 0 && !showWelcome && (
        <div className="suggestions">
          <p>Try asking me:</p>
          <div className="suggestion-buttons">
            {suggestions.map((suggestion, index) => (
              <button 
                key={index} 
                className="suggestion-button"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
      
      <form onSubmit={handleSendMessage} className="input-area">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type your message here..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
};

export default ChatbotInterface;