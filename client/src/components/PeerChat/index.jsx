import React, { useState, useEffect, useRef, useContext } from 'react';
import { io } from 'socket.io-client';
import { AuthContext } from '../../context/AuthContext';
import { Send, Users, UserPlus } from 'lucide-react';

const PeerChat = () => {
  const { user } = useContext(AuthContext);
  const [socket, setSocket] = useState(null);
  const [room, setRoom] = useState('Global Study Room');
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Connect to Socket
    const newSocket = io('http://localhost:5001');
    setSocket(newSocket);

    newSocket.emit('join_study_room', room);

    newSocket.on('receive_message', (data) => {
      setMessages((prev) => [...prev, data]);
    });

    return () => {
      newSocket.disconnect();
    };
  }, [room]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = (e) => {
    e.preventDefault();
    if (message.trim() && socket) {
      const messageData = {
        room,
        message,
        username: user?.username || 'Anonymous',
        collegeName: user?.collegeName || 'Unknown College',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      socket.emit('send_message', messageData);
      setMessage('');
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-gray-200 dark:border-slate-700 overflow-hidden">
      
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-800/50">
        <div className="flex items-center space-x-3">
          <div className="bg-primary-100 dark:bg-primary-900/30 p-2 rounded-full">
            <Users className="text-primary-600 dark:text-primary-400" size={24} />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900 dark:text-white">{room}</h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">Connect with peers</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400 dark:text-gray-500">
            <Users size={48} className="mb-4 opacity-50" />
            <p>No messages yet. Start the conversation!</p>
          </div>
        ) : (
          messages.map((msg, idx) => {
            const isMe = msg.username === user?.username;
            return (
              <div key={idx} className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}>
                <span className="text-xs text-gray-500 dark:text-gray-400 mb-1 ml-1 flex items-center space-x-1">
                  <span className="font-semibold">{isMe ? 'You' : msg.username}</span>
                  {!isMe && msg.collegeName && (
                    <span className="bg-gray-200 dark:bg-slate-700 px-1.5 py-0.5 rounded text-[10px]">
                      {msg.collegeName}
                    </span>
                  )}
                </span>
                <div className={`px-4 py-2 rounded-2xl max-w-[80%] ${
                  isMe 
                    ? 'bg-primary-600 text-white rounded-tr-none' 
                    : 'bg-gray-100 dark:bg-slate-700 text-gray-800 dark:text-gray-100 rounded-tl-none'
                }`}>
                  <p>{msg.message}</p>
                </div>
                <span className="text-[10px] text-gray-400 mt-1">{msg.timestamp}</span>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 bg-white dark:bg-slate-800 border-t border-gray-200 dark:border-slate-700">
        <form onSubmit={sendMessage} className="flex space-x-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type a message to the room..."
            className="flex-1 rounded-full border border-gray-300 dark:border-slate-600 bg-gray-50 dark:bg-slate-700 px-4 py-3 text-gray-900 dark:text-white focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
          />
          <button
            type="submit"
            disabled={!message.trim()}
            className="p-3 rounded-full bg-primary-600 text-white flex-shrink-0 hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            <Send size={20} />
          </button>
        </form>
      </div>

    </div>
  );
};

export default PeerChat;
