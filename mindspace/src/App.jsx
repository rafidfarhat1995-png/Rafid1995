import { useState } from 'react';
import './index.css';
import ApiKeySetup from './components/ApiKeySetup';
import ChatWindow from './components/ChatWindow';

function App() {
  const [apiKey, setApiKey] = useState(() => sessionStorage.getItem('ms_key') || '');

  function handleSaveKey(key) {
    sessionStorage.setItem('ms_key', key);
    setApiKey(key);
  }

  function handleLogout() {
    sessionStorage.removeItem('ms_key');
    setApiKey('');
  }

  if (!apiKey) {
    return <ApiKeySetup onSave={handleSaveKey} />;
  }

  return <ChatWindow apiKey={apiKey} onLogout={handleLogout} />;
}

export default App;
