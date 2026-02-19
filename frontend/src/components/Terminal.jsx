import React, { useEffect, useRef } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';
import './Terminal.css';

const TerminalComponent = () => {
    const terminalRef = useRef(null);
    const xtermRef = useRef(null);
    const socketRef = useRef(null);
    const fitAddonRef = useRef(null);

    useEffect(() => {
        // Initialize xterm
        const term = new Terminal({
            cursorBlink: true,
            theme: {
                background: '#1e1e1e',
                foreground: '#d4d4d4',
                cursor: '#d4d4d4',
                selection: '#264f78',
                black: '#1e1e1e',
                red: '#f48771',
                green: '#89d185',
                yellow: '#cca700',
                blue: '#40a6ff',
                magenta: '#c586c0',
                cyan: '#007acc',
                white: '#d4d4d4',
                brightBlack: '#808080',
                brightRed: '#f48771',
                brightGreen: '#89d185',
                brightYellow: '#cca700',
                brightBlue: '#40a6ff',
                brightMagenta: '#c586c0',
                brightCyan: '#007acc',
                brightWhite: '#ffffff',
            },
            fontFamily: 'Consolas, "Courier New", monospace',
            fontSize: 14,
        });

        const fitAddon = new FitAddon();
        term.loadAddon(fitAddon);

        if (terminalRef.current) {
            term.open(terminalRef.current);
            fitAddon.fit();
        }

        xtermRef.current = term;
        fitAddonRef.current = fitAddon;

        // Connect to WebSocket
        const socket = new WebSocket('ws://localhost:8000/api/ws/terminal');
        socketRef.current = socket;

        socket.onopen = () => {
            term.write('\r\n\x1b[32mConnected to Multi-Agent IDE Terminal\x1b[0m\r\n');
            // Sending an enter key to provoke a prompt
            socket.send('\r');
        };

        socket.onmessage = (event) => {
            term.write(event.data);
        };

        socket.onclose = () => {
            term.write('\r\n\x1b[31mConnection closed\x1b[0m\r\n');
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            term.write('\r\n\x1b[31mConnection error\x1b[0m\r\n');
        };

        // Send input to WebSocket
        term.onData((data) => {
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(data);
            }
        });

        // Handle resize
        const handleResize = () => {
            fitAddon.fit();
        };
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            socket.close();
            term.dispose();
        };
    }, []);

    return (
        <div className="terminal-container" ref={terminalRef} />
    );
};

export default TerminalComponent;
