import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Trash2, FileText, Loader } from 'lucide-react';

const Notes = () => {
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [subject, setSubject] = useState('');
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);

  const fetchNotes = async () => {
    try {
      const res = await axios.get('http://localhost:5001/api/notes');
      setNotes(res.data);
    } catch (err) {
      console.error('Error fetching notes', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  const handleCreateNote = async (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;

    try {
      const res = await axios.post('http://localhost:5001/api/notes', {
        title, content, subject: subject || 'General'
      });
      setNotes([res.data, ...notes]);
      setTitle('');
      setContent('');
      setSubject('');
      setIsCreating(false);
    } catch (err) {
      console.error('Error creating note', err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://localhost:5001/api/notes/${id}`);
      setNotes(notes.filter(n => n._id !== id));
    } catch (err) {
      console.error('Error deleting note', err);
    }
  };

  if (loading) {
    return <div className="flex h-full items-center justify-center"><Loader className="animate-spin text-primary-500" size={48} /></div>;
  }

  return (
    <div className="h-full flex flex-col space-y-6">
      
      {/* Header and Add Button */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Study Notes</h2>
          <p className="text-gray-500 dark:text-gray-400">Keep track of your learning</p>
        </div>
        <button 
          onClick={() => setIsCreating(!isCreating)}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors shadow-sm"
        >
          {isCreating ? 'Cancel' : <><Plus size={18} className="mr-2" /> New Note</>}
        </button>
      </div>

      {/* Create Note Form */}
      {isCreating && (
        <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-slate-700 animate-in fade-in slide-in-from-top-4">
          <form onSubmit={handleCreateNote} className="space-y-4">
            <div className="flex space-x-4">
              <input
                type="text"
                placeholder="Note Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="flex-1 rounded-lg border border-gray-300 dark:border-slate-600 bg-gray-50 dark:bg-slate-700 px-4 py-2 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
              <input
                type="text"
                placeholder="Subject (Optional)"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-1/3 rounded-lg border border-gray-300 dark:border-slate-600 bg-gray-50 dark:bg-slate-700 px-4 py-2 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <textarea
              placeholder="Start typing your notes here..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full rounded-lg border border-gray-300 dark:border-slate-600 bg-gray-50 dark:bg-slate-700 px-4 py-3 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[150px]"
              required
            />
            <div className="flex justify-end">
              <button
                type="submit"
                className="px-6 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
              >
                Save Note
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Notes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 overflow-y-auto pb-6">
        {notes.length === 0 && !isCreating ? (
          <div className="col-span-full flex flex-col items-center justify-center p-12 text-gray-400">
            <FileText size={64} className="mb-4 opacity-30" />
            <p className="text-lg">No notes found. Create your first study note!</p>
          </div>
        ) : (
          notes.map(note => (
            <div key={note._id} className="bg-white dark:bg-slate-800 p-5 rounded-2xl shadow-sm border border-gray-200 dark:border-slate-700 flex flex-col hover:shadow-md transition-shadow group">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-bold text-lg text-gray-900 dark:text-white line-clamp-1">{note.title}</h3>
                <button 
                  onClick={() => handleDelete(note._id)}
                  className="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 size={18} />
                </button>
              </div>
              <span className="inline-block bg-primary-100 text-primary-800 dark:bg-primary-900/40 dark:text-primary-300 text-xs px-2 py-1 rounded mb-3 self-start">
                {note.subject}
              </span>
              <p className="text-gray-600 dark:text-gray-400 flex-1 whitespace-pre-wrap line-clamp-5 text-sm">
                {note.content}
              </p>
              <div className="mt-4 text-xs text-gray-400 pt-3 border-t border-gray-100 dark:border-slate-700/50">
                {new Date(note.createdAt).toLocaleDateString()}
              </div>
            </div>
          ))
        )}
      </div>

    </div>
  );
};

export default Notes;
