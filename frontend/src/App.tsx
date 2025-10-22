import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import LiveMetrics from './pages/LiveMetrics';
import HMIEmbed from './pages/HMIEmbed';
import { useState, useEffect } from 'react';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if token exists in localStorage
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (token: string) => {
    localStorage.setItem('token', token);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  return (
    <Router>
      <div className="app">
        {isAuthenticated && (
          <nav style={{ padding: '1rem', background: '#1a1a1a', marginBottom: '1rem' }}>
            <a href="/metrics" style={{ marginRight: '1rem', color: '#646cff' }}>Live Metrics</a>
            <a href="/hmi" style={{ marginRight: '1rem', color: '#646cff' }}>HMI Interface</a>
            <button onClick={handleLogout}>Logout</button>
          </nav>
        )}
        
        <Routes>
          <Route 
            path="/login" 
            element={
              isAuthenticated ? 
              <Navigate to="/metrics" /> : 
              <Login onLogin={handleLogin} />
            } 
          />
          <Route 
            path="/metrics" 
            element={
              isAuthenticated ? 
              <LiveMetrics /> : 
              <Navigate to="/login" />
            } 
          />
          <Route 
            path="/hmi" 
            element={
              isAuthenticated ? 
              <HMIEmbed /> : 
              <Navigate to="/login" />
            } 
          />
          <Route path="/" element={<Navigate to="/metrics" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
