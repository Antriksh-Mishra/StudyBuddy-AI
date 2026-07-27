import React, { useState, useContext, useEffect } from 'react';
import { Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Bot, MessageSquare, BookOpen, Clock, LogOut, Menu, X, Moon, Sun } from 'lucide-react';

import AIChat from '../components/AIChat';
import PeerChat from '../components/PeerChat';
import Notes from '../components/Notes';
import StudyTimer from '../components/StudyTimer';

const Dashboard = () => {
  const { user, logout } = useContext(AuthContext);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('theme') === 'dark');
  const location = useLocation();

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.body.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  const navItems = [
    { name: 'AI Assistant', path: '/dashboard', icon: <Bot size={20} /> },
    { name: 'Study Timer', path: '/dashboard/timer', icon: <Clock size={20} /> },
    { name: 'Notes', path: '/dashboard/notes', icon: <BookOpen size={20} /> },
    { name: 'Peer Chat', path: '/dashboard/chat', icon: <MessageSquare size={20} /> },
  ];

  return (
    <div className="min-h-screen flex bg-gray-100 dark:bg-slate-900 transition-colors duration-300">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:static lg:inset-0 z-30 w-64 glass dark:glass-dark text-gray-900 dark:text-white transition duration-300 ease-in-out border-r border-gray-200 dark:border-slate-800 flex flex-col`}>
        <div className="p-6 flex items-center justify-between border-b border-gray-200 dark:border-slate-700/50">
          <h2 className="text-2xl font-bold text-primary-600 dark:text-primary-400">StudyBuddy AI</h2>
          <button className="lg:hidden" onClick={() => setSidebarOpen(false)}>
            <X size={24} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-primary-500 text-white' 
                    : 'hover:bg-gray-200 dark:hover:bg-slate-800'
                }`}
              >
                {item.icon}
                <span className="ml-3 font-medium">{item.name}</span>
              </Link>
            );
          })}
        </div>

        <div className="p-4 border-t border-gray-200 dark:border-slate-700/50">
          <div className="flex items-center justify-between mb-4 px-2">
            <span className="text-sm text-gray-500 dark:text-gray-400 truncate">
              {user?.username} ({user?.collegeName})
            </span>
            <button 
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-slate-800 transition-colors"
            >
              {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>
          <button
            onClick={logout}
            className="flex items-center w-full px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
          >
            <LogOut size={18} className="mr-2" />
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="lg:hidden bg-white dark:bg-slate-800 shadow-sm border-b border-gray-200 dark:border-slate-700 p-4 flex items-center">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 focus:outline-none"
          >
            <Menu size={24} />
          </button>
          <h1 className="ml-4 text-xl font-semibold text-gray-900 dark:text-white">StudyBuddy AI</h1>
        </header>

        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <Routes>
            <Route path="/" element={<AIChat />} />
            <Route path="/timer" element={<StudyTimer />} />
            <Route path="/notes" element={<Notes />} />
            <Route path="/chat" element={<PeerChat />} />
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
