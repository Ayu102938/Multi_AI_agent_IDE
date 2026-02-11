import { useState } from 'react'
import Editor from '@monaco-editor/react'
import axios from 'axios'
import './App.css'

function App() {
  const [code, setCode] = useState('// Type your code here')
  const [output, setOutput] = useState('')

  const handleRunCode = async () => {
    try {
      const response = await axios.get('http://localhost:8000/')
      setOutput(`Backend Status: ${response.data.status}\n\nRunning code: \n${code}`)
    } catch (error) {
      setOutput(`Error connecting to backend: ${error.message}`)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw' }}>
      <div style={{ padding: '10px', backgroundColor: '#1e1e1e', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Multi-Agent IDE</h2>
        <button onClick={handleRunCode} style={{ padding: '8px 16px', backgroundColor: '#007acc', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Run Code
        </button>
      </div>
      <div style={{ display: 'flex', flex: 1 }}>
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
    </div>
  )
}

export default App
