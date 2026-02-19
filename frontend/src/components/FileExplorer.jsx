// frontend/src/components/FileExplorer.jsx
import { useState, useEffect } from 'react';
import axios from 'axios';
import './FileExplorer.css';

function FileExplorer({ onFileSelect }) {
    const [files, setFiles] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchFiles();
        const interval = setInterval(fetchFiles, 5000); // Poll every 5 seconds
        return () => clearInterval(interval);
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

    const handleDelete = async (e, filename) => {
        e.stopPropagation(); // Prevent file selection when clicking delete
        if (!window.confirm(`Are you sure you want to delete ${filename}?`)) return;

        try {
            await axios.delete(`http://localhost:8000/api/files/${filename}`);
            fetchFiles(); // Refresh list immediately
        } catch (err) {
            console.error("Error deleting file:", err);
            alert("Failed to delete file");
        }
    };

    return (
        <div className="file-explorer">
            <h3>Workspace Files</h3>
            {error && <div className="error">{error}</div>}
            <button onClick={fetchFiles} className="refresh-btn">Refresh</button>
            <ul className="file-list">
                {files.map((file) => (
                    <li key={file} onClick={() => onFileSelect(file)} className="file-item">
                        <span className="file-name">{file}</span>
                        <button
                            className="delete-btn"
                            onClick={(e) => handleDelete(e, file)}
                            title="Delete file"
                        >
                            ×
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default FileExplorer;
