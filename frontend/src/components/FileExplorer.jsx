// frontend/src/components/FileExplorer.jsx
import { useState, useEffect } from 'react';
import axios from 'axios';
import './FileExplorer.css';

function FileExplorer({ onFileSelect }) {
    const [files, setFiles] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchFiles();
    }, []);

    const fetchFiles = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/files');
            setFiles(response.data.files);
        } catch (err) {
            console.error("Error fetching files:", err);
            setError("Failed to load files");
        }
    };

    return (
        <div className="file-explorer">
            <h3>Workspace Files</h3>
            {error && <div className="error">{error}</div>}
            <button onClick={fetchFiles} className="refresh-btn">Refresh</button>
            <ul className="file-list">
                {files.map((file) => (
                    <li key={file} onClick={() => onFileSelect(file)}>
                        {file}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default FileExplorer;
