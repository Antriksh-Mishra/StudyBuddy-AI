import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, Coffee, BookOpen } from 'lucide-react';

const StudyTimer = () => {
  const FOCUS_TIME = 25 * 60; // 25 minutes in seconds
  const BREAK_TIME = 5 * 60; // 5 minutes in seconds

  const [timeLeft, setTimeLeft] = useState(FOCUS_TIME);
  const [isActive, setIsActive] = useState(false);
  const [isBreak, setIsBreak] = useState(false);
  const [sessionsCompleted, setSessionsCompleted] = useState(0);

  useEffect(() => {
    let interval = null;
    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (isActive && timeLeft === 0) {
      // Timer finished
      if (!isBreak) {
        setSessionsCompleted(c => c + 1);
        setIsBreak(true);
        setTimeLeft(BREAK_TIME);
      } else {
        setIsBreak(false);
        setTimeLeft(FOCUS_TIME);
      }
      setIsActive(false);
      
      // Play sound
      const audio = new Audio('/notification.mp3'); // Assuming we'd have this file
      audio.play().catch(e => console.log('Audio play failed', e));
    }
    return () => clearInterval(interval);
  }, [isActive, timeLeft, isBreak]);

  const toggleTimer = () => setIsActive(!isActive);

  const resetTimer = () => {
    setIsActive(false);
    setIsBreak(false);
    setTimeLeft(FOCUS_TIME);
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const progress = isBreak 
    ? ((BREAK_TIME - timeLeft) / BREAK_TIME) * 100 
    : ((FOCUS_TIME - timeLeft) / FOCUS_TIME) * 100;

  return (
    <div className="flex flex-col h-full items-center justify-center p-6 bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-gray-200 dark:border-slate-700">
      
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center justify-center">
          {isBreak ? <Coffee className="mr-3 text-amber-500" /> : <BookOpen className="mr-3 text-primary-500" />}
          {isBreak ? 'Break Time' : 'Focus Session'}
        </h2>
        <p className="text-gray-500 dark:text-gray-400">
          Stay productive. Sessions completed today: <span className="font-bold text-primary-600 dark:text-primary-400">{sessionsCompleted}</span>
        </p>
      </div>

      <div className="relative w-72 h-72 mb-10">
        {/* Circular Progress */}
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle
            className="text-gray-200 dark:text-slate-700 stroke-current"
            strokeWidth="4"
            cx="50"
            cy="50"
            r="48"
            fill="transparent"
          />
          <circle
            className={`${isBreak ? 'text-amber-500' : 'text-primary-600'} stroke-current transition-all duration-1000 ease-linear`}
            strokeWidth="4"
            strokeLinecap="round"
            cx="50"
            cy="50"
            r="48"
            fill="transparent"
            strokeDasharray={`${progress * 3.01} 999`} // ~2*PI*R
          />
        </svg>
        
        {/* Time Display */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
          <span className="text-6xl font-extrabold text-gray-900 dark:text-white tabular-nums tracking-tight">
            {formatTime(timeLeft)}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-center space-x-6">
        <button
          onClick={toggleTimer}
          className={`h-16 w-16 rounded-full flex items-center justify-center text-white shadow-lg transition-transform hover:scale-105 ${
            isActive 
              ? 'bg-amber-500 hover:bg-amber-400' 
              : 'bg-primary-600 hover:bg-primary-500'
          }`}
        >
          {isActive ? <Pause size={32} /> : <Play size={32} className="ml-1" />}
        </button>
        
        <button
          onClick={resetTimer}
          className="h-16 w-16 rounded-full flex items-center justify-center bg-gray-200 text-gray-700 dark:bg-slate-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-slate-600 shadow-lg transition-transform hover:scale-105"
        >
          <RotateCcw size={28} />
        </button>
      </div>

    </div>
  );
};

export default StudyTimer;
