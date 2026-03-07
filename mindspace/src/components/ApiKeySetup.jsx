import { KeyRound, ExternalLink } from 'lucide-react';
import { useState } from 'react';

export default function ApiKeySetup({ onSave }) {
  const [key, setKey] = useState('');
  const [error, setError] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = key.trim();
    if (!trimmed.startsWith('sk-ant-')) {
      setError('That doesn\'t look like a valid Anthropic API key. It should start with sk-ant-');
      return;
    }
    setError('');
    onSave(trimmed);
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 to-slate-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-lg p-8 w-full max-w-md">
        <div className="flex items-center justify-center w-14 h-14 bg-teal-100 rounded-2xl mb-6 mx-auto">
          <KeyRound className="text-teal-600" size={24} />
        </div>

        <h1 className="text-2xl font-bold text-slate-800 text-center mb-2">MindSpace</h1>
        <p className="text-slate-500 text-center text-sm mb-6">
          Your private AI wellness companion
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Anthropic API Key
            </label>
            <input
              type="password"
              value={key}
              onChange={e => setKey(e.target.value)}
              placeholder="sk-ant-..."
              className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-400 focus:border-transparent"
              autoComplete="off"
            />
            {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
          </div>

          <button
            type="submit"
            className="w-full bg-teal-600 hover:bg-teal-700 text-white font-semibold py-3 rounded-xl transition-colors"
          >
            Start Session
          </button>
        </form>

        <p className="text-xs text-slate-400 text-center mt-4">
          Your key is stored only in your browser session and never sent anywhere except directly to Anthropic.
        </p>

        <a
          href="https://console.anthropic.com/account/keys"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-1 text-xs text-teal-600 hover:text-teal-700 mt-3"
        >
          Get a free API key <ExternalLink size={10} />
        </a>

        <div className="mt-6 pt-5 border-t border-slate-100">
          <p className="text-xs text-slate-400 text-center">
            ⚠️ MindSpace is not a substitute for professional mental health care.
            If you&apos;re in crisis, call or text <strong>988</strong>.
          </p>
        </div>
      </div>
    </div>
  );
}
