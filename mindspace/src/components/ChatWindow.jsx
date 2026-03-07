import { useState, useRef, useEffect } from 'react';
import { Send, RefreshCw, LogOut } from 'lucide-react';
import Message from './Message';
import CrisisBanner from './CrisisBanner';
import { sendMessage, detectCrisis } from '../api/claude';

const WELCOME_MESSAGE = {
  role: 'assistant',
  content: "Hi, I'm glad you're here. This is a safe space — no judgment, just support. What's been on your mind lately?",
  id: 'welcome',
};

export default function ChatWindow({ apiKey, onLogout }) {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showCrisis, setShowCrisis] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    if (detectCrisis(text)) setShowCrisis(true);

    const userMsg = { role: 'user', content: text, id: Date.now() };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    const assistantId = Date.now() + 1;
    const streamingMsg = { role: 'assistant', content: '', streaming: true, id: assistantId };
    setMessages(prev => [...prev, streamingMsg]);

    try {
      const apiMessages = updatedMessages
        .filter(m => m.id !== 'welcome')
        .map(m => ({ role: m.role, content: m.content }));

      const stream = await sendMessage(apiMessages, apiKey);

      let fullText = '';
      for await (const event of stream) {
        if (
          event.type === 'content_block_delta' &&
          event.delta.type === 'text_delta'
        ) {
          fullText += event.delta.text;
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantId ? { ...m, content: fullText } : m
            )
          );
        }
      }

      // Check if AI response also mentions crisis signals to show banner
      if (detectCrisis(fullText)) setShowCrisis(true);

      setMessages(prev =>
        prev.map(m =>
          m.id === assistantId ? { ...m, streaming: false } : m
        )
      );
    } catch (err) {
      console.error(err);
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantId
            ? { ...m, content: 'Sorry, something went wrong. Please try again.', streaming: false }
            : m
        )
      );
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleReset() {
    setMessages([WELCOME_MESSAGE]);
    setShowCrisis(false);
    setInput('');
    inputRef.current?.focus();
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 to-slate-100 flex flex-col items-center py-6 px-4">
      {/* Header */}
      <div className="w-full max-w-2xl mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-800">MindSpace</h1>
          <p className="text-xs text-slate-500">Your private wellness companion</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700 bg-white border border-slate-200 px-3 py-1.5 rounded-lg transition-colors"
            title="New session"
          >
            <RefreshCw size={12} />
            New chat
          </button>
          <button
            onClick={onLogout}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700 bg-white border border-slate-200 px-3 py-1.5 rounded-lg transition-colors"
            title="Logout"
          >
            <LogOut size={12} />
            Logout
          </button>
        </div>
      </div>

      {/* Chat card */}
      <div className="w-full max-w-2xl bg-white rounded-3xl shadow-lg flex flex-col overflow-hidden" style={{ height: 'calc(100vh - 130px)' }}>
        {/* Messages area */}
        <div className="flex-1 overflow-y-auto p-4 pt-5">
          {messages.map(msg => (
            <Message key={msg.id} message={msg} />
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Crisis banner */}
        <CrisisBanner visible={showCrisis} />

        {/* Disclaimer */}
        <div className="px-4 pb-1">
          <p className="text-xs text-slate-400 text-center">
            Not a substitute for professional care · Crisis line: <strong>988</strong>
          </p>
        </div>

        {/* Input area */}
        <div className="p-3 border-t border-slate-100">
          <div className="flex gap-2 items-end bg-slate-50 rounded-2xl px-4 py-2">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Share what's on your mind..."
              rows={1}
              className="flex-1 bg-transparent resize-none text-sm text-slate-700 placeholder-slate-400 outline-none py-1 max-h-32"
              style={{ lineHeight: '1.5' }}
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="bg-teal-600 hover:bg-teal-700 disabled:bg-slate-200 disabled:cursor-not-allowed text-white p-2 rounded-xl transition-colors shrink-0 mb-0.5"
            >
              <Send size={16} />
            </button>
          </div>
          <p className="text-xs text-slate-400 text-center mt-1.5">
            Press Enter to send · Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}
