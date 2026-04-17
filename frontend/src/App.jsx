import React from 'react';
import DashboardPage from './pages/DashboardPage';
import DeveloperPage from './pages/DeveloperPage';
import './App.css';

const App = () => {
  const isDeveloperPage = window.location.pathname === '/developer';

  return isDeveloperPage ? <DeveloperPage /> : <DashboardPage />;
};

export default App;
