import { useState, useEffect, useRef } from 'react'
import Editor from '@monaco-editor/react'
import axios from 'axios'
import FileExplorer from './components/FileExplorer'
import TerminalComponent from './components/Terminal'
import './App.css'

function App() {
  const [code, setCode] = useState('// Type your code here')
  const [output, setOutput] = useState('')
  const [message, setMessage] = useState('')
  const [inputVal, setInputVal] = useState('') // User input for running code
  const [chatHistory, setChatHistory] = useState([])
  const [activityLogs, setActivityLogs] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)

  // Use a Ref to store the latest timestamp to avoid re-creating the interval
  const lastTimestampRef = useRef(null);

  // Poll for activity logs
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const timestamp = lastTimestampRef.current;
        const url = timestamp ? `http://localhost:8000/api/activity?after=${timestamp}` : 'http://localhost:8000/api/activity';

        const response = await axios.get(url);
        if (response.data.logs && response.data.logs.length > 0) {
          const newLogs = response.data.logs;

          let hasNew = false;
          // De-duplicate in place if needed, but timestamp filtering should handle it.
          // Still good to update the ref.
          const lastLog = newLogs[newLogs.length - 1];
          if (lastLog) {
            lastTimestampRef.current = lastLog.timestamp;
            hasNew = true;
          }

          if (hasNew) {
            setActivityLogs(prev => {
              // Double check for duplicates
              const existingIds = new Set(prev.map(l => l.timestamp));
              const uniqueNew = newLogs.filter(l => !existingIds.has(l.timestamp));
              if (uniqueNew.length === 0) return prev;

              // Helper to check for completion within the update
              const combined = [...prev, ...uniqueNew];

              // Check completion logic
              const completionLog = uniqueNew.find(log =>
                (log.role === 'System' && (log.message.includes('Workflow complete!') || log.message.includes('Error during execution'))) ||
                log.message.includes('All tasks completed (Demo)')
              );
              if (completionLog) {
                setIsProcessing(false);
              }

              // Check code updates
              const codeLog = uniqueNew.find(log => log.type === 'code');
              if (codeLog) {
                setCode(codeLog.message);
              }

              return combined;
            });
          }
        }
      } catch (error) {
        console.error("Failed to fetch activity logs", error);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []); // Empty dependency!


  const handleRunCode = async () => {
    setOutput("Running...");
    try {
      const response = await axios.post('http://localhost:8000/api/run', {
        code: code,
        input: inputVal
      });
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

    setIsProcessing(true);

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
      setIsProcessing(false);
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
            <button
              onClick={handleSendMessage}
              disabled={isProcessing}
              style={{
                padding: '5px 10px',
                backgroundColor: isProcessing ? '#444' : '#0e639c',
                color: isProcessing ? '#888' : 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: isProcessing ? 'not-allowed' : 'pointer'
              }}
            >
              Send
            </button>
          </div>
        </div>

        {/* Main Content Area: Editor + Terminal */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div style={{ flex: 1 }}>
            <Editor
              height="100%"
              defaultLanguage="python"
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value)}
            />
          </div>
          {/* Terminal Area */}
          <div style={{ height: '30%', minHeight: '200px', borderTop: '1px solid #3e3e42', backgroundColor: '#1e1e1e' }}>
            <div style={{ padding: '5px 10px', backgroundColor: '#252526', color: '#ccc', fontSize: '12px', borderBottom: '1px solid #3e3e42', display: 'flex', justifyContent: 'space-between' }}>
              <span>TERMINAL</span>
              {/* Optional: Add clear button or status here */}
            </div>
            <div style={{ height: 'calc(100% - 28px)' }}>
              <TerminalComponent />
            </div>
          </div>
        </div>
      </div>

      {/* Activity Log Panel */}
      <div style={{ height: '150px', backgroundColor: '#1e1e1e', color: '#ccc', borderTop: '1px solid #3e3e42', padding: '10px', overflowY: 'auto', fontFamily: 'monospace', fontSize: '12px' }}>
        <h4 style={{ margin: '0 0 5px 0', display: 'flex', alignItems: 'center' }}>
          Agent Activity Log
          {isProcessing && <span style={{ marginLeft: '10px', fontSize: '0.9em', color: '#4ec9b0', display: 'flex', alignItems: 'center' }}><span className="spinner"></span> Thinking...</span>}
        </h4>
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

