"""
Progress tracking helper for real-time WebSocket updates
"""
import asyncio
import time
from threading import Thread

class ProgressTracker:
    """Tracks agent progress and sends WebSocket updates"""
    
    def __init__(self, job_id, ws_send_func):
        self.job_id = job_id
        self.ws_send = ws_send_func
        self.start_time = time.time()
        self.current_agent = None
        self.agent_start_time = None
        
        # Estimated durations for each agent (adjust based on your system)
        self.agent_durations = {
            'Research Agent': 40,
            'Writer Agent': 80,
            'Editor Agent': 30,
            'SEO Agent': 20
        }
        
        self.total_duration = sum(self.agent_durations.values())
        self.agents = list(self.agent_durations.keys())
        self.current_agent_index = 0
        self.monitoring = False
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        self.monitoring = True
        Thread(target=self._monitor_progress, daemon=True).start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
    
    def _monitor_progress(self):
        """Monitor and send progress updates"""
        total_progress = 0
        
        for idx, agent_name in enumerate(self.agents):
            if not self.monitoring:
                break
            
            # Mark agent as active
            asyncio.run(self.ws_send(self.job_id, {
                'type': 'agent_update',
                'agent': agent_name,
                'status': 'active',
                'progress': 0,
                'message': f'{agent_name} started'
            }))
            
            agent_duration = self.agent_durations[agent_name]
            steps = 10
            
            # Send progress updates for this agent
            for step in range(steps + 1):
                if not self.monitoring:
                    break
                
                progress = int((step / steps) * 100)
                total_progress = int(((idx + step/steps) / len(self.agents)) * 100)
                
                asyncio.run(self.ws_send(self.job_id, {
                    'type': 'agent_progress',
                    'agent': agent_name,
                    'progress': progress,
                    'total_progress': total_progress,
                    'message': f'{agent_name}: {progress}% complete'
                }))
                
                time.sleep(agent_duration / steps)
            
            # Mark agent complete
            elapsed = time.time() - self.start_time
            asyncio.run(self.ws_send(self.job_id, {
                'type': 'agent_update',
                'agent': agent_name,
                'status': 'complete',
                'progress': 100,
                'time': round(agent_duration, 1),
                'message': f'{agent_name} completed'
            }))
    
    def mark_complete(self):
        """Mark all agents complete"""
        self.stop_monitoring()
        
        for agent_name in self.agents:
            asyncio.run(self.ws_send(self.job_id, {
                'type': 'agent_update',
                'agent': agent_name,
                'status': 'complete',
                'progress': 100
            }))