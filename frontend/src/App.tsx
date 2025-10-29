<<<<<<< HEAD
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import LiveMetrics from './pages/LiveMetrics';
import AIAssistant from './pages/AIAssistant';
import { useState, useEffect } from 'react';
=======
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Devices from "./pages/Devices";
import Monitoring from "./pages/Monitoring";
import History from "./pages/History";
import Signals from "./pages/Signals";
import Status from "./pages/Status";
import NotFound from "./pages/NotFound";
>>>>>>> feature/Web

const queryClient = new QueryClient();

<<<<<<< HEAD
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
            <a href="/ai" style={{ marginRight: '1rem', color: '#646cff' }}>AI Assistant</a>
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
            path="/ai"
            element={
              isAuthenticated ?
                <AIAssistant /> :
                <Navigate to="/login" />
            }
          />
          <Route path="/" element={<Navigate to="/metrics" />} />
        </Routes>
      </div>
    </Router>
  );
}
=======
const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<Login />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/devices"
              element={
                <ProtectedRoute>
                  <Devices />
                </ProtectedRoute>
              }
            />
            <Route
              path="/monitoring"
              element={
                <ProtectedRoute>
                  <Monitoring />
                </ProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <History />
                </ProtectedRoute>
              }
            />
            <Route
              path="/signals"
              element={
                <ProtectedRoute>
                  <Signals />
                </ProtectedRoute>
              }
            />
            <Route
              path="/status"
              element={
                <ProtectedRoute>
                  <Status />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);
>>>>>>> feature/Web

export default App;
