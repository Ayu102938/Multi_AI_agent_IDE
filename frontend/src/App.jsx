import { useState, useEffect } from 'react'
import Editor from '@monaco-editor/react'
import axios from 'axios'
import FileExplorer from './components/FileExplorer'
import './App.css'

function App() {
  const [code, setCode] = useState('// Type your code here')
  const [output, setOutput] = useState('')
  const [message, setMessage] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [activityLogs, setActivityLogs] = useState([])

  // Poll for activity logs
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const lastLog = activityLogs[activityLogs.length - 1];
        const timestamp = lastLog ? lastLog.timestamp : null;
        const url = timestamp ? `http://localhost:8000/api/activity?after=${timestamp}` : 'http://localhost:8000/api/activity';

        const response = await axios.get(url);
        if (response.data.logs && response.data.logs.length > 0) {
          const newLogs = response.data.logs;
          setActivityLogs(prev => [...prev, ...newLogs]);

          // Check for code updates
          const codeLog = newLogs.find(log => log.type === 'code');
          if (codeLog) {
            setCode(codeLog.message);
          }
        }
      } catch (error) {
        console.error("Failed to fetch activity logs", error);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [activityLogs]);

  const handleRunCode = async () => {
    setOutput("Running...");
    try {
      const response = await axios.post('http://localhost:8000/api/run', { code: code });
      if (response.data.status === 'success') {
        setOutput(response.data.output);
      } else {
        setOutput(`Error:\n${response.data.output}`);
      }
    } catch (error) {
      setOutput(`Failed to execute code: ${error.message}`);
    }
  }

  const handleFileSelect = async (filename) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/files/${filename}`);
      if (response.data.content) {
        setCode(response.data.content);
      }
    } catch (error) {
      console.error("Error reading file:", error);
      setOutput(`Failed to read file: ${error.message}`);
    }
  }

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    const newUserMsg = { role: 'user', content: message };
    setChatHistory(prev => [...prev, newUserMsg]);
    setMessage('');

    try {
      const response = await axios.post('http://localhost:8000/api/chat', { message: message });
      const newAiMsg = { role: 'ai', content: response.data.response };
      setChatHistory(prev => [...prev, newAiMsg]);
    } catch (error) {
      const errorMsg = { role: 'system', content: `Error: ${error.message}` };
      setChatHistory(prev => [...prev, errorMsg]);
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100%', boxSizing: 'border-box' }}>
      <div style={{ padding: '10px', backgroundColor: '#1e1e1e', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>Multi-Agent IDE</h2>
        <button onClick={handleRunCode} style={{ padding: '8px 16px', backgroundColor: '#007acc', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Run Code
        </button>
      </div>
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <FileExplorer onFileSelect={handleFileSelect} />
        <div style={{ width: '300px', backgroundColor: '#252526', color: '#d4d4d4', padding: '10px', display: 'flex', flexDirection: 'column', borderRight: '1px solid #3e3e42' }}>
          <h3>Chat</h3>
          <div style={{ flex: 1, overflowY: 'auto', marginBottom: '10px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {chatHistory.map((msg, index) => (
              <div key={index} style={{
                padding: '8px',
                borderRadius: '4px',
                backgroundColor: msg.role === 'user' ? '#3e3e42' : '#007acc',
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '90%'
              }}>
                {msg.content}
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', gap: '5px' }}>
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              style={{ flex: 1, padding: '5px', borderRadius: '4px', border: 'none' }}
              placeholder="Ask AI..."
            />
            <button onClick={handleSendMessage} style={{ padding: '5px 10px', backgroundColor: '#0e639c', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Send</button>
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <Editor
            height="100%"
            defaultLanguage="python"
            theme="vs-dark"
            value={code}
            onChange={(value) => setCode(value)}
          />
        </div>
        <div style={{ width: '300px', backgroundColor: '#252526', color: '#d4d4d4', padding: '10px', borderLeft: '1px solid #3e3e42', overflowY: 'auto' }}>
          <h3>Output</h3>
          <pre>{output}</pre>
        </div>
      </div>

      {/* Activity Log Panel */}
      <div style={{ height: '150px', backgroundColor: '#1e1e1e', color: '#ccc', borderTop: '1px solid #3e3e42', padding: '10px', overflowY: 'auto', fontFamily: 'monospace', fontSize: '12px' }}>
        <h4 style={{ margin: '0 0 5px 0' }}>Agent Activity Log</h4>
        {activityLogs.map((log, index) => (
          <div key={index} style={{ marginBottom: '2px' }}>
            <span style={{ color: '#569cd6' }}>[{log.timestamp.split('T')[1].split('.')[0]}]</span>{' '}
            <span style={{ color: '#4ec9b0', fontWeight: 'bold' }}>{log.role}</span>:{' '}
            <span style={{ color: log.type === 'error' ? '#f48771' : log.type === 'thought' ? '#ce9178' : '#d4d4d4' }}>
              {log.message}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App
