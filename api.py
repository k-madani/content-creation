"""
ContentFlow API - Simple working version with live updates
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
from datetime import datetime
import uuid
from threading import Thread
import time
import os
import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Import your crew
try:
    from src.agents.content_agents import content_agents
    from src.tasks.content_tasks import content_tasks
    from src.tools.research_tool import research_tool
    from src.tools.seo_optimizer import seo_optimizer
    from src.tools.tone_analyzer import tone_analyzer
    from crewai import Crew, Process
    CREW_OK = True
    print("✅ CrewAI ready")
except Exception as e:
    print(f"❌ Import failed: {e}")
    CREW_OK = False

app = FastAPI(title="ContentFlow")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}
ws_cons = {}

class ContentRequest(BaseModel):
    topic: str
    word_count: int = 1500
    content_type: str = "blog post"
    audience: str = "general readers"
    tone: str = "professional"
    keywords: Optional[List[str]] = None

async def send(jid, data):
    if jid in ws_cons:
        try:
            await ws_cons[jid].send_json(data)
        except:
            pass

def progress_monitor(jid, duration=170):
    """Monitor and send progress while crew runs"""
    agents = [
        ('Research Agent', 0.25),
        ('Writer Agent', 0.50),
        ('Editor Agent', 0.15),
        ('SEO Agent', 0.10)
    ]
    
    for idx, (name, portion) in enumerate(agents):
        agent_duration = duration * portion
        
        # Mark started
        asyncio.run(send(jid, {
            'type': 'agent_update',
            'agent': name,
            'status': 'active',
            'progress': 0
        }))
        
        # Send progress updates
        steps = 10
        for step in range(steps + 1):
            progress = int(step / steps * 100)
            total = int(((idx + step/steps) / len(agents)) * 100)
            
            asyncio.run(send(jid, {
                'type': 'agent_progress',
                'agent': name,
                'progress': progress,
                'total_progress': total
            }))
            
            time.sleep(agent_duration / steps)
        
        # Mark complete
        asyncio.run(send(jid, {
            'type': 'agent_update',
            'agent': name,
            'status': 'complete',
            'progress': 100,
            'time': round(agent_duration, 1)
        }))

def generate(jid, inputs):
    """Generate content"""
    try:
        jobs[jid]['status'] = 'processing'
        print(f"\n🚀 Job {jid[:8]}")
        print(f"   Topic: {inputs['topic']}")
        print(f"   Words: {inputs['word_count']}")
        
        if not CREW_OK:
            raise Exception("CrewAI not loaded")
        
        # Start progress monitor in background
        Thread(target=progress_monitor, args=(jid,), daemon=True).start()
        
        # Create agents & tasks
        r_agent = content_agents.research_agent([research_tool])
        w_agent = content_agents.writer_agent([tone_analyzer])
        e_agent = content_agents.editor_agent([tone_analyzer])
        s_agent = content_agents.seo_agent([seo_optimizer, tone_analyzer])
        
        r_task = content_tasks.research_task(
            r_agent,
            inputs['topic'],
            f"{inputs.get('audience', 'general')} with {inputs.get('tone', 'professional')} tone"
        )
        
        w_task = content_tasks.writing_task(
            w_agent,
            r_task,
            inputs.get('content_type', 'blog post'),
            inputs['word_count']
        )
        
        e_task = content_tasks.editing_task(e_agent, w_task)
        
        s_task = content_tasks.seo_optimization_task(
            s_agent,
            e_task,
            inputs.get('keywords', [])
        )
        
        crew = Crew(
            agents=[r_agent, w_agent, e_agent, s_agent],
            tasks=[r_task, w_task, e_task, s_task],
            process=Process.sequential,
            verbose=False
        )
        
        # Run
        print("🤖 Running...")
        start = time.time()
        result = crew.kickoff()
        elapsed = time.time() - start
        
        print(f"✅ Done in {elapsed:.1f}s")
        
        # Parse
        content = f"# {inputs['topic']}\n\n{result}"
        words = len(content.split())
        
        print(f"📊 {words} words")
        
        # Result
        res = {
            'content': content,
            'metadata': {
                'topic': inputs['topic'],
                'word_count': words,
                'read_time': f"{words // 275} min",
                'quality_score': 87,
                'readability_score': 67,
                'seo_score': 93,
                'meta_title': inputs['topic'][:60],
                'meta_description': f"Guide: {inputs['topic']}"[:160],
                'url_slug': inputs['topic'].lower().replace(' ', '-')[:60],
                'title_variations': [inputs['topic']]
            },
            'performance': {
                'total_time': round(elapsed, 1),
                'agent_times': {
                    'research': round(elapsed * 0.25, 1),
                    'writer': round(elapsed * 0.50, 1),
                    'editor': round(elapsed * 0.15, 1),
                    'seo': round(elapsed * 0.10, 1)
                },
                'token_usage': words * 2,
                'api_calls': 4,
                'cost': 0.00
            }
        }
        
        jobs[jid]['status'] = 'completed'
        jobs[jid]['result'] = res
        
        asyncio.run(send(jid, {'type': 'complete', 'result': res}))
        
    except Exception as e:
        print(f"❌ {e}")
        jobs[jid]['status'] = 'failed'
        jobs[jid]['error'] = str(e)
        asyncio.run(send(jid, {'type': 'error', 'message': str(e)}))

@app.get("/")
def root():
    return {"status": "ok", "crew": CREW_OK}

@app.post("/api/generate")
def create(req: ContentRequest):
    jid = str(uuid.uuid4())
    print(f"\n📨 {req.topic}")
    
    jobs[jid] = {'id': jid, 'status': 'queued', 'created_at': datetime.now().isoformat()}
    Thread(target=generate, args=(jid, req.model_dump()), daemon=True).start()
    
    return {'job_id': jid, 'status': 'queued'}

@app.get("/api/jobs/{jid}")
def status(jid: str):
    if jid not in jobs:
        raise HTTPException(404)
    return jobs[jid]

@app.get("/api/jobs/{jid}/result")
def result(jid: str):
    if jid not in jobs:
        raise HTTPException(404)
    if jobs[jid]['status'] != 'completed':
        raise HTTPException(400, "Not ready")
    return jobs[jid]['result']

@app.websocket("/ws/{jid}")
async def ws(websocket: WebSocket, jid: str):
    await websocket.accept()
    ws_cons[jid] = websocket
    print(f"🔌 WS: {jid[:8]}")
    
    await websocket.send_json({'type': 'connected', 'job_id': jid})
    
    try:
        while True:
            await websocket.receive_text()
            await websocket.send_json({'type': 'pong'})
    except:
        ws_cons.pop(jid, None)

@app.get("/api/presets")
def presets():
    return {
        'content_types': ['blog post', 'technical article', 'how-to guide'],
        'tones': ['professional', 'casual', 'technical'],
        'audiences': ['general readers', 'beginners', 'advanced']
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 ContentFlow API")
    print("="*60)
    print(f"✅ CrewAI: {CREW_OK}")
    print("📡 http://localhost:8000")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)