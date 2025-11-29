import React, { useState, useEffect, useRef } from 'react';
import AgentCard from '../components/AgentCard';
import ProgressBar from '../components/ProgressBar';
import { API_URL, WS_URL, AGENT_DURATIONS } from '../utils/constants';

export default function PipelinePage({ jobId, onNavigate }) {
  const [agents, setAgents] = useState([
    { name: 'Research Agent', status: 'queued', progress: 0, time: 0 },
    { name: 'Writer Agent', status: 'queued', progress: 0, time: 0 },
    { name: 'Editor Agent', status: 'queued', progress: 0, time: 0 },
    { name: 'SEO Agent', status: 'queued', progress: 0, time: 0 }
  ]);
  
  const [totalProgress, setTotalProgress] = useState(0);
  const [logs, setLogs] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const startTime = useRef(Date.now());
  const wsRef = useRef(null);
  const pollIntervalRef = useRef(null);

  useEffect(() => {
    if (!jobId) return;

    console.log(`📡 Connecting to job ${jobId}`);
    
    // Try WebSocket connection
    connectWebSocket();
    
    // Also poll for status as backup
    startPolling();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [jobId]);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket(`${WS_URL}/ws/${jobId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        setConnectionStatus('connected');
        addLog('WebSocket connected');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('📨 WebSocket message:', data);
        handleWebSocketMessage(data);
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setConnectionStatus('error');
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket closed');
        setConnectionStatus('disconnected');
      };
    } catch (error) {
      console.error('❌ WebSocket connection failed:', error);
      setConnectionStatus('error');
    }
  };

  const startPolling = () => {
    // Poll job status every 2 seconds as backup
    pollIntervalRef.current = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/api/jobs/${jobId}`);
        if (response.ok) {
          const status = await response.json();
          
          if (status.status === 'completed') {
            clearInterval(pollIntervalRef.current);
            fetchResultAndNavigate();
          } else if (status.status === 'failed') {
            clearInterval(pollIntervalRef.current);
            addLog(`Error: ${status.error || 'Generation failed'}`);
          }
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 2000);
  };

  const fetchResultAndNavigate = async () => {
    try {
      addLog('Fetching results...');
      const response = await fetch(`${API_URL}/api/jobs/${jobId}/result`);
      
      if (response.ok) {
        const result = await response.json();
        addLog('✓ Results received');
        
        // Navigate to results page
        setTimeout(() => {
          onNavigate('results', { result });
        }, 1000);
      }
    } catch (error) {
      console.error('Failed to fetch result:', error);
      addLog(`Error: ${error.message}`);
    }
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'connected':
        addLog('Connected to generation service');
        break;
        
      case 'agent_update':
        updateAgent(data.agent, data.status, data.progress || 0, data.time || 0);
        addLog(`${data.agent}: ${data.message || data.status}`);
        break;
        
      case 'agent_progress':
        updateAgentProgress(data.agent, data.progress);
        if (data.total_progress) {
          setTotalProgress(data.total_progress);
        }
        break;
        
      case 'complete':
        addLog('✓ Generation complete!');
        setTotalProgress(100);
        markAllComplete();
        
        setTimeout(() => {
          onNavigate('results', { result: data.result });
        }, 1000);
        break;
        
      case 'error':
        addLog(`✗ Error: ${data.message}`);
        break;
        
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const updateAgent = (agentName, status, progress, time) => {
    setAgents(prev => prev.map(agent => 
      agent.name === agentName 
        ? { ...agent, status, progress: progress || agent.progress, time: time || agent.time }
        : agent
    ));
  };

  const updateAgentProgress = (agentName, progress) => {
    setAgents(prev => prev.map(agent =>
      agent.name === agentName
        ? { ...agent, progress }
        : agent
    ));
  };

  const markAllComplete = () => {
    setAgents(prev => prev.map(agent => ({
      ...agent,
      status: 'complete',
      progress: 100
    })));
  };

  const addLog = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { time: timestamp, message }].slice(-20));
  };

  const estimatedTime = Math.max(0, 180 - Math.floor((Date.now() - startTime.current) / 1000));

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Generation in Progress</h2>
        <p className="text-slate-600 dark:text-slate-400">Job #{jobId?.slice(0, 8)}</p>
        {connectionStatus !== 'connected' && (
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Status: {connectionStatus === 'connecting' ? 'Connecting...' : 'Polling for updates'}
          </p>
        )}
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <ProgressBar 
          progress={totalProgress} 
          label="Overall Progress"
          estimatedTime={estimatedTime}
        />
      </div>

      {/* Agent Pipeline */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 mb-6 shadow-sm">
        <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-4">Agent Pipeline</h3>
        <div className="space-y-4">
          {agents.map((agent, index) => (
            <AgentCard key={index} agent={agent} index={index} />
          ))}
        </div>
      </div>

      {/* Live Console */}
      <div className="bg-slate-900 dark:bg-slate-950 rounded-2xl p-6 border border-slate-800 dark:border-slate-700 shadow-sm">
        <h3 className="text-sm font-bold text-slate-400 mb-3 uppercase tracking-wide flex items-center gap-2">
          <div className="w-2 h-2 bg-accent-500 rounded-full animate-pulse" />
          System Console
        </h3>
        <div className="space-y-2 font-mono text-xs h-64 overflow-y-auto">
          {logs.length === 0 ? (
            <div className="text-slate-500">Waiting for updates...</div>
          ) : (
            logs.map((log, i) => (
              <div key={i} className="flex gap-3">
                <span className="text-slate-500">[{log.time}]</span>
                <span className="text-accent-400">{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}