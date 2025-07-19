import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import './App.css';
import { fetchAgents } from './lib/api';

function Home() {
  return (
    <div>
      <h2>Welcome to the AI Agent Boardroom</h2>
      <p>Navigate through the links above to manage agents and sessions.</p>
    </div>
  );
}

function Agents() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getAgents = async () => {
      try {
        const data = await fetchAgents();
        setAgents(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    getAgents();
  }, []);

  if (loading) return <p>Loading agents...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <div>
      <h2>AI Agents</h2>
      {agents.length === 0 ? (
        <p>No agents found.</p>
      ) : (
        <ul>
          {agents.map((agent) => (
            <li key={agent.id}>
              <strong>{agent.name}</strong> ({agent.authority_level})
              <p>{agent.description}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Sessions() {
  return (
    <div>
      <h2>Boardroom Sessions</h2>
      <p>List of boardroom sessions will be displayed here.</p>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>AI Agent Boardroom</h1>
          <nav>
            <ul>
              <li><Link to="/">Home</Link></li>
              <li><Link to="/agents">Agents</Link></li>
              <li><Link to="/sessions">Sessions</Link></li>
            </ul>
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/sessions" element={<Sessions />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;


