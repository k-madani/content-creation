"""
FastAPI Server for ContentForge
Provides REST API with Server-Sent Events for real-time progress
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json
import uuid
from datetime import datetime
import sys
import os
from pathlib import Path

# Add parent directory to path to import main.py modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="ContentForge API", version="1.0.0")

# CORS - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite + React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active generation jobs
active_jobs = {}

class GenerateRequest(BaseModel):
    topic: str
    tone: str = "professional"
    wordCount: int = 1200
    keywords: List[str] = []
    title: Optional[str] = None

class GenerateResponse(BaseModel):
    jobId: str
    status: str
    message: str

# Progress tracking
class ProgressTracker:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.current_stage = None
        self.stages = {
            'research': {'status': 'pending', 'progress': 0},
            'writing': {'status': 'pending', 'progress': 0},
            'editing': {'status': 'pending', 'progress': 0},
            'seo': {'status': 'pending', 'progress': 0}
        }
        self.messages = []
    
    def update_stage(self, stage: str, status: str, progress: int, message: str = ""):
        self.current_stage = stage
        self.stages[stage]['status'] = status
        self.stages[stage]['progress'] = progress
        
        event = {
            'type': 'progress',
            'stage': stage,
            'status': status,
            'progress': progress,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.messages.append(event)
        return event
    
    def complete_stage(self, stage: str):
        return self.update_stage(stage, 'complete', 100, f"{stage.title()} complete ✓")
    
    def error_stage(self, stage: str, error: str):
        return self.update_stage(stage, 'error', 0, f"Error: {error}")


async def generate_content_stream(job_id: str, config: dict):
    """
    Generate content with progress streaming
    """
    tracker = ProgressTracker(job_id)
    
    try:
        # Send initial status
        yield f"data: {json.dumps({'type': 'start', 'jobId': job_id, 'message': 'Starting generation...'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Stage 1: Research
        yield f"data: {json.dumps(tracker.update_stage('research', 'working', 10, 'Starting research phase...'))}\n\n"
        await asyncio.sleep(1)
        
        yield f"data: {json.dumps(tracker.update_stage('research', 'working', 50, 'Gathering data from sources...'))}\n\n"
        await asyncio.sleep(2)
        
        # Import and run actual generation
        from main import generate_single_attempt
        from utils.user_input import UserInputCollector
        
        # Simulate research completion
        yield f"data: {json.dumps(tracker.complete_stage('research'))}\n\n"
        await asyncio.sleep(0.5)
        
        # Stage 2: Writing
        yield f"data: {json.dumps(tracker.update_stage('writing', 'working', 10, 'Creating content draft...'))}\n\n"
        await asyncio.sleep(1)
        
        yield f"data: {json.dumps(tracker.update_stage('writing', 'working', 60, 'Writing main content...'))}\n\n"
        
        # Run actual content generation in background
        # For now, simulate with sleep - we'll integrate real generation next
        await asyncio.sleep(3)
        
        yield f"data: {json.dumps(tracker.complete_stage('writing'))}\n\n"
        await asyncio.sleep(0.5)
        
        # Stage 3: Editing
        yield f"data: {json.dumps(tracker.update_stage('editing', 'working', 30, 'Refining content...'))}\n\n"
        await asyncio.sleep(2)
        
        yield f"data: {json.dumps(tracker.complete_stage('editing'))}\n\n"
        await asyncio.sleep(0.5)
        
        # Stage 4: SEO
        yield f"data: {json.dumps(tracker.update_stage('seo', 'working', 40, 'Optimizing for search engines...'))}\n\n"
        await asyncio.sleep(2)
        
        yield f"data: {json.dumps(tracker.complete_stage('seo'))}\n\n"
        await asyncio.sleep(0.5)
        
        # Final result
        result = {
            'type': 'complete',
            'jobId': job_id,
            'content': f"# {config.get('title', config['topic'])}\n\nGenerated content will appear here...\n\n[This is a test response. Real generation coming next!]",
            'metadata': {
                'wordCount': 1200,
                'qualityScore': 85,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        yield f"data: {json.dumps(result)}\n\n"
        
    except Exception as e:
        error_event = {
            'type': 'error',
            'jobId': job_id,
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }
        yield f"data: {json.dumps(error_event)}\n\n"


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    """
    Start content generation and return job ID
    """
    job_id = str(uuid.uuid4())
    
    config = {
        'topic': request.topic,
        'tone': request.tone,
        'word_count': request.wordCount,
        'keywords': request.keywords,
        'title': request.title or request.topic
    }
    
    active_jobs[job_id] = {
        'status': 'queued',
        'config': config,
        'created_at': datetime.now().isoformat()
    }
    
    return GenerateResponse(
        jobId=job_id,
        status="queued",
        message="Generation job created successfully"
    )


@app.get("/api/generate/{job_id}/stream")
async def stream_progress(job_id: str):
    """
    Stream generation progress using Server-Sent Events
    """
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    config = active_jobs[job_id]['config']
    active_jobs[job_id]['status'] = 'processing'
    
    return StreamingResponse(
        generate_content_stream(job_id, config),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "activeJobs": len(active_jobs)
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ContentForge API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )