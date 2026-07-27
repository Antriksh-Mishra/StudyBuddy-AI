# StudyBuddy AI

A full-stack, real-time AI-powered study platform where students can collaborate and interact with an AI assistant using text and voice.

## Tech Stack
- **Frontend**: React + Vite + Tailwind CSS v4
- **Backend**: Node.js + Express
- **Database**: MongoDB (Mongoose)
- **Authentication**: JWT
- **Real-time**: Socket.io
- **AI**: Google Gemini API
- **Voice**: Web Speech API

## Setup Instructions

### 1. Prerequisites
- Node.js (v18+ recommended)
- MongoDB running locally (or change the `MONGO_URI` to a cloud instance)

### 2. Backend Setup
1. Open a terminal and navigate to the `server` directory:
   ```bash
   cd server
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Set your **Gemini API Key** in `server/.env`:
   ```env
   PORT=5000
   MONGO_URI=mongodb://127.0.0.1:27017/studybuddy
   JWT_SECRET=supersecretjwtkey123
   GEMINI_API_KEY=YOUR_ACTUAL_API_KEY_HERE
   ```
4. Start the backend development server:
   ```bash
   npm run dev
   ```

### 3. Frontend Setup
1. Open a new terminal and navigate to the `client` directory:
   ```bash
   cd client
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

### 4. Features Included
- **AI Chatbot**: Uses Google Gemini API to answer study questions. Click the Mic icon to speak your questions, and the AI will respond via text and voice.
- **Peer Chat**: Real-time study rooms using Socket.io to connect with other students.
- **Study Timer**: A built-in Pomodoro timer (25 min focus / 5 min break) with a beautiful circular progress indicator.
- **Study Notes**: Save, view, and organize your study notes, stored in MongoDB.
- **Authentication**: JWT-based secure authentication with Registration Number and College Name support.
- **Dark Mode**: Beautiful dark and light mode UI designed with Tailwind CSS and glassmorphism.
