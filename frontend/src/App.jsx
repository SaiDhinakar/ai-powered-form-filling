import { Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Entities from './pages/Entities';
import FormFilling from './pages/FormFilling';
import Templates from './pages/Templates';
import RecentForms from './pages/RecentForms';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    // Check if token exists
    return !!localStorage.getItem('token');
  });

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.setItem('isAuthenticated', 'false');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <Layout onLogout={handleLogout}>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/entities" element={<Entities />} />
        <Route path="/form-filling" element={<FormFilling />} />
        <Route path="/templates" element={<Templates />} />
        <Route path="/recent-forms" element={<RecentForms />} />
      </Routes>
    </Layout>
  );
}

export default App;
