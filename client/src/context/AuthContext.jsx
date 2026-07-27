import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // Hardcode a mock user and token to bypass login
  const [user, setUser] = useState({
    _id: 'mock_id',
    username: 'Guest Student',
    email: 'guest@example.com',
    collegeName: 'Demo College',
    registrationNumber: '123456'
  });
  const [token, setToken] = useState('mock-token');
  const [loading, setLoading] = useState(false);

  const register = async (userData) => {
    // Mock register
  };

  const login = async (userData) => {
    // Mock login
  };

  const logout = () => {
    // Mock logout - usually would redirect or reset, but for now just do nothing
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, register, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
