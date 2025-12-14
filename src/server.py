"""
FastAPI Server for ContentForge
WITH REALISTIC TIMING matching actual backend (163s total)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json
import uuid
from datetime import datetime
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="ContentForge API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated images
output_images_dir = Path("outputs/images")
output_images_dir.mkdir(exist_ok=True, parents=True)
app.mount("/images", StaticFiles(directory=str(output_images_dir)), name="images")

active_jobs = {}

class GenerateRequest(BaseModel):
    topic: str
    tone: str = "professional"
    wordCount: int = 1200
    keywords: List[str] = []
    title: Optional[str] = None
    includeImages: bool = False
    imageCount: int = 3

class GenerateResponse(BaseModel):
    jobId: str
    status: str
    message: str

class ProgressTracker:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.current_stage = None
        self.stages = {
            'research': {'status': 'pending', 'progress': 0},
            'writing': {'status': 'pending', 'progress': 0},
            'editing': {'status': 'pending', 'progress': 0},
            'seo': {'status': 'pending', 'progress': 0},
            'images': {'status': 'pending', 'progress': 0}
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


def generate_mock_article(topic: str, title: str, target_word_count: int, tone: str) -> str:
    """Generate mock article matching target word count"""
    
    sections = [
        {
            'title': 'Introduction',
            'paragraphs': [
                f"{topic} represents a fundamental shift in how we approach modern challenges and opportunities. This comprehensive guide explores the key concepts, practical applications, and future implications that make this subject essential for today's landscape.",
                f"Understanding {topic} requires examining both theoretical foundations and real-world implementations. As industries continue to evolve, mastering these concepts becomes increasingly critical for professionals and enthusiasts alike.",
                f"In this detailed exploration, we'll uncover the core principles, examine practical strategies, and provide actionable insights that you can apply immediately. Whether you're just starting or looking to deepen your expertise, this guide offers valuable perspectives."
            ]
        },
        {
            'title': 'Understanding the Fundamentals',
            'paragraphs': [
                f"The foundation of {topic} lies in understanding both its theoretical underpinnings and practical applications. By examining the core principles, we can better appreciate how this field has evolved and where it's headed.",
                "At its core, this domain encompasses several interconnected concepts that work together to create comprehensive solutions. Each element plays a crucial role in the overall ecosystem, contributing unique value and functionality.",
                "Historical context provides valuable insights into current practices. By understanding how methodologies have evolved, we can better anticipate future developments and position ourselves strategically."
            ]
        },
        {
            'title': 'Key Concepts and Principles',
            'paragraphs': [
                "Several fundamental concepts form the backbone of modern approaches. First, pattern recognition and analysis enable us to identify trends and make data-driven decisions. This capability has become increasingly sophisticated with technological advancement.",
                "Second, systematic problem-solving approaches provide frameworks for tackling complex challenges. These methodologies have been refined over decades, incorporating lessons learned from countless implementations across diverse industries.",
                "Third, continuous improvement methodologies ensure that systems remain adaptive and responsive. This iterative approach allows organizations to evolve alongside changing market conditions and technological capabilities.",
                "Additionally, collaborative frameworks enable teams to work together effectively, leveraging diverse expertise and perspectives. This human element remains crucial despite increasing automation."
            ]
        },
        {
            'title': 'Practical Applications and Use Cases',
            'paragraphs': [
                f"Real-world implementation of {topic} spans numerous industries and contexts. In enterprise environments, these approaches drive operational efficiency and strategic decision-making. Organizations report significant improvements in productivity and outcomes.",
                "Small and medium-sized businesses benefit equally, though their implementation strategies may differ. Scalable solutions allow organizations of all sizes to leverage advanced capabilities without overwhelming resources or complexity.",
                "Individual practitioners and enthusiasts also find value in understanding these concepts. Personal projects and learning initiatives demonstrate the accessibility and broad applicability of fundamental principles.",
                "Case studies from leading organizations illustrate successful implementation patterns. These examples provide valuable templates that others can adapt to their specific contexts and requirements."
            ]
        },
        {
            'title': 'Technical Implementation and Architecture',
            'paragraphs': [
                "When implementing solutions, architecture plays a crucial role in long-term success. Well-designed systems prioritize modularity, scalability, maintainability, and security from the outset.",
                "Modern approaches leverage cloud-based infrastructure, enabling flexible resource allocation and global accessibility. This shift from traditional on-premises solutions offers significant advantages in terms of cost, reliability, and innovation speed.",
                "API-first architecture has become standard practice, facilitating integration between diverse systems and services. This approach supports the composable enterprise model, where organizations assemble best-of-breed solutions.",
                "Microservices design patterns enable independent development and deployment of system components. This architectural style supports rapid iteration and reduces the risk associated with large-scale changes.",
                "Container orchestration platforms provide robust deployment and management capabilities. These tools have revolutionized how organizations build, test, and deploy applications at scale."
            ]
        },
        {
            'title': 'Best Practices and Methodologies',
            'paragraphs': [
                "Successful implementation requires adherence to established best practices. Start with clear requirements and specifications, ensuring all stakeholders share a common understanding of objectives and constraints.",
                "Version control and code review processes maintain code quality and facilitate collaboration. These practices have become fundamental to modern development workflows, regardless of team size or project scope.",
                "Comprehensive testing strategies catch issues early and ensure reliability. Automated testing frameworks enable rapid feedback loops, allowing teams to iterate quickly while maintaining quality standards.",
                "Continuous integration and continuous deployment (CI/CD) pipelines streamline the path from development to production. These automated workflows reduce manual effort and minimize the risk of human error.",
                "Monitoring and observability tools provide visibility into system behavior and performance. Real-time insights enable proactive issue resolution and informed optimization decisions."
            ]
        },
        {
            'title': 'Advanced Strategies and Techniques',
            'paragraphs': [
                f"As practitioners advance in their understanding of {topic}, they can leverage more sophisticated strategies. Advanced techniques build upon foundational knowledge, offering enhanced capabilities and efficiency.",
                "Optimization approaches focus on improving performance, reducing costs, and maximizing value. These strategies often involve careful analysis of bottlenecks and strategic resource allocation.",
                "Integration with emerging technologies opens new possibilities. Organizations that successfully combine traditional approaches with innovative capabilities gain significant competitive advantages.",
                "Automation strategies reduce manual effort and improve consistency. Well-designed automated workflows handle routine tasks, freeing human resources for higher-value activities.",
                "Data-driven decision-making leverages analytics and insights to guide strategy. Organizations increasingly rely on quantitative analysis to validate assumptions and measure outcomes."
            ]
        },
        {
            'title': 'Common Challenges and Solutions',
            'paragraphs': [
                "Every implementation faces obstacles. Understanding common challenges helps teams prepare and respond effectively. The most frequent issues relate to complexity management, resource constraints, and organizational resistance.",
                "Complexity management requires clear documentation, modular design, and regular refactoring. Teams that invest in maintainability find it easier to evolve their systems over time.",
                "Technical debt accumulates when shortcuts are taken during development. Allocating dedicated time for code cleanup and modernization prevents debt from becoming overwhelming.",
                "Skill gaps challenge many organizations. Investing in training, encouraging knowledge sharing, and building communities of practice helps teams develop necessary capabilities.",
                "Integration with legacy systems often proves difficult. Using API gateways, implementing adapters, and planning gradual migrations can ease this transition."
            ]
        },
        {
            'title': 'Industry Trends and Future Outlook',
            'paragraphs': [
                f"The landscape of {topic} continues to evolve rapidly. Several key trends shape the direction of future development and adoption.",
                "Artificial intelligence and machine learning integration represents one of the most significant shifts. Intelligent automation and predictive analytics are becoming standard features rather than premium add-ons.",
                "Edge computing moves processing closer to data sources, reducing latency and enabling new use cases. This distributed approach complements traditional cloud computing models.",
                "Serverless architectures allow developers to focus on business logic without managing infrastructure. This paradigm shift continues to gain traction across various application types.",
                "Low-code and no-code platforms democratize development capabilities. These tools enable broader participation in solution creation, though they complement rather than replace traditional development.",
                "Sustainability considerations increasingly influence technology decisions. Energy efficiency and environmental impact factor into architectural and implementation choices."
            ]
        },
        {
            'title': 'Implementation Roadmap',
            'paragraphs': [
                "Successful implementation follows a structured approach. The journey typically progresses through several distinct phases, each with specific objectives and deliverables.",
                "The foundation phase focuses on assessment, planning, and preparation. Teams evaluate current state, define success metrics, and establish necessary infrastructure and processes.",
                "During the development phase, core features are built and tested. Iterative approaches allow for regular feedback and adjustment, ensuring the solution meets actual needs.",
                "The optimization phase refines performance and addresses identified issues. Teams focus on stability, efficiency, and user experience improvements.",
                "Ongoing scaling and evolution ensures the solution remains relevant. Continuous monitoring, feedback collection, and strategic enhancement maintain long-term value."
            ]
        },
        {
            'title': 'Measuring Success and ROI',
            'paragraphs': [
                "Defining and tracking key performance indicators (KPIs) enables objective evaluation of outcomes. Metrics should align with strategic objectives and provide actionable insights.",
                "System uptime and reliability metrics indicate operational health. Targeting 99.9% uptime has become standard for production systems, with many organizations achieving even higher levels.",
                "Performance metrics like response time and throughput directly impact user experience. Regular monitoring and optimization ensure these metrics remain within acceptable ranges.",
                "User engagement indicators reveal how effectively solutions meet needs. High engagement typically correlates with successful implementation and strong value delivery.",
                "Business impact measurements connect technical outcomes to organizational objectives. Demonstrating return on investment (ROI) justifies continued investment and guides future priorities."
            ]
        },
        {
            'title': 'Conclusion',
            'paragraphs': [
                f"{topic} continues to transform industries and create new possibilities. Success requires a combination of technical expertise, strategic thinking, and continuous learning.",
                "By following best practices, staying informed about emerging trends, and maintaining a focus on real-world value delivery, organizations and individuals can leverage these concepts to achieve significant advantages.",
                "The journey from understanding fundamentals to mastering advanced techniques is continuous. Whether you're just starting or looking to deepen your expertise, the key is to remain curious, experiment boldly, and learn from both successes and failures.",
                "As you move forward, remember that implementation is as important as understanding. Take action, iterate based on results, and don't be afraid to adjust your approach as you learn.",
                "The future holds exciting possibilities. By building strong foundations today and remaining adaptable to change, you'll be well-positioned to capitalize on emerging opportunities and navigate evolving challenges."
            ]
        }
    ]
    
    # Build article
    article_parts = [f"# {title}\n"]
    current_word_count = len(title.split())
    
    for section in sections:
        article_parts.append(f"\n## {section['title']}\n")
        current_word_count += len(section['title'].split())
        
        for para in section['paragraphs']:
            article_parts.append(f"\n{para}\n")
            current_word_count += len(para.split())
            
            if current_word_count >= target_word_count * 0.95:
                break
        
        if current_word_count >= target_word_count * 0.95:
            break
    
    # Add more if still short
    if current_word_count < target_word_count * 0.95:
        additional_para = f"Furthermore, continued exploration of {topic} reveals additional nuances and opportunities. Organizations that invest in deep understanding and strategic implementation consistently outperform those taking superficial approaches. This investment in knowledge and capability development pays dividends across multiple dimensions, from operational efficiency to innovation capacity. The commitment to excellence in this domain separates leaders from followers."
        article_parts.append(f"\n{additional_para}\n")
    
    return ''.join(article_parts)


async def generate_content_stream(job_id: str, config: dict):
    """
    REALISTIC TIMING: Matches actual backend execution (~163 seconds total)
    Based on real CrewAI output timing
    """
    tracker = ProgressTracker(job_id)
    
    try:
        yield f"data: {json.dumps({'type': 'start', 'jobId': job_id, 'message': 'Starting generation...'})}\n\n"
        await asyncio.sleep(2)
        
        # =====================================
        # STAGE 1: RESEARCH (~40 seconds)
        # Real: Multiple Wikipedia/DDG searches
        # =====================================
        yield f"data: {json.dumps(tracker.update_stage('research', 'working', 5, 'Initializing research tools...'))}\n\n"
        await asyncio.sleep(3)
        
        yield f"data: {json.dumps(tracker.update_stage('research', 'working', 15, 'Searching Wikipedia for topic...'))}\n\n"
        await asyncio.sleep(6)
        
        yield f"data: {json.dumps(tracker.update_stage('research', 'working', 30, 'Querying DuckDuckGo for current data...'))}\n\n"
        await asyncio.sleep(7)
        
        yield f"data: {json.dumps(tracker.update_stage('research', 'working', 50, 'Analyzing search results...'))}\n\n"
        await asyncio.sleep(8)
        
        yield f"data: {json.dumps(tracker.update_stage('research', 'working', 70, 'Gathering additional sources...'))}\n\n"
        await asyncio.sleep(7)
        
        yield f"data: {json.dumps(tracker.update_stage('research', 'working', 90, 'Compiling research findings...'))}\n\n"
        await asyncio.sleep(7)
        
        yield f"data: {json.dumps(tracker.complete_stage('research'))}\n\n"
        await asyncio.sleep(2)
        
        # =====================================
        # STAGE 2: WRITING (~60 seconds)
        # Real: AI generating 1200-2000 words
        # =====================================
        yield f"data: {json.dumps(tracker.update_stage('writing', 'working', 5, 'Analyzing tone requirements...'))}\n\n"
        await asyncio.sleep(5)
        
        yield f"data: {json.dumps(tracker.update_stage('writing', 'working', 15, 'Creating content outline...'))}\n\n"
        await asyncio.sleep(6)
        
        yield f"data: {json.dumps(tracker.update_stage('writing', 'working', 25, 'Writing introduction...'))}\n\n"
        await asyncio.sleep(8)
        
        yield f"data: {json.dumps(tracker.update_stage('writing', 'working', 40, 'Developing section 1 of 5...'))}\n\n"
        await asyncio.sleep(7)
        
        yield f"data: {json.dumps(tracker.update_stage('writing', 'working', 55, 'Developing section 2 of 5...'))}\n\n"
        await asyncio.sleep(8)
        
        yield f"data: {json.dumps(tracker.update_stage('writing', 'working', 70, 'Developing section 3 of 5...'))}\n\n"
        await asyncio.sleep(9)
        
        yield f"data: {json.dumps(tracker.update_stage('writing', 'working', 85, 'Writing conclusion and call-to-action...'))}\n\n"
        await asyncio.sleep(12)
        
        yield f"data: {json.dumps(tracker.update_stage('writing', 'working', 95, 'Finalizing draft...'))}\n\n"
        await asyncio.sleep(5)
        
        yield f"data: {json.dumps(tracker.complete_stage('writing'))}\n\n"
        await asyncio.sleep(2)
        
        # =====================================
        # STAGE 3: EDITING (~35 seconds)
        # Real: AI refining content
        # =====================================
        yield f"data: {json.dumps(tracker.update_stage('editing', 'working', 10, 'Analyzing content structure...'))}\n\n"
        await asyncio.sleep(5)
        
        yield f"data: {json.dumps(tracker.update_stage('editing', 'working', 25, 'Checking grammar and spelling...'))}\n\n"
        await asyncio.sleep(6)
        
        yield f"data: {json.dumps(tracker.update_stage('editing', 'working', 45, 'Improving clarity and flow...'))}\n\n"
        await asyncio.sleep(8)
        
        yield f"data: {json.dumps(tracker.update_stage('editing', 'working', 65, 'Refining language and tone...'))}\n\n"
        await asyncio.sleep(7)
        
        yield f"data: {json.dumps(tracker.update_stage('editing', 'working', 85, 'Strengthening conclusion...'))}\n\n"
        await asyncio.sleep(6)
        
        yield f"data: {json.dumps(tracker.update_stage('editing', 'working', 95, 'Final polish...'))}\n\n"
        await asyncio.sleep(3)
        
        yield f"data: {json.dumps(tracker.complete_stage('editing'))}\n\n"
        await asyncio.sleep(2)
        
        # =====================================
        # STAGE 4: SEO (~20 seconds)
        # Real: Keyword analysis and optimization
        # =====================================
        yield f"data: {json.dumps(tracker.update_stage('seo', 'working', 10, 'Analyzing current keyword density...'))}\n\n"
        await asyncio.sleep(4)
        
        yield f"data: {json.dumps(tracker.update_stage('seo', 'working', 30, 'Optimizing header structure...'))}\n\n"
        await asyncio.sleep(5)
        
        yield f"data: {json.dumps(tracker.update_stage('seo', 'working', 50, 'Generating meta tags...'))}\n\n"
        await asyncio.sleep(4)
        
        yield f"data: {json.dumps(tracker.update_stage('seo', 'working', 70, 'Creating URL slug...'))}\n\n"
        await asyncio.sleep(4)
        
        yield f"data: {json.dumps(tracker.update_stage('seo', 'working', 90, 'Finalizing SEO optimizations...'))}\n\n"
        await asyncio.sleep(3)
        
        yield f"data: {json.dumps(tracker.complete_stage('seo'))}\n\n"
        await asyncio.sleep(2)
        
        # Generate article
        topic = config.get('topic', 'Technology Trends')
        title = config.get('title') or f"Mastering {topic}: A Comprehensive Guide"
        word_count = config.get('word_count', 1200)
        tone = config.get('tone', 'professional')
        
        mock_article = generate_mock_article(topic, title, word_count, tone)
        
        # =====================================
        # STAGE 5: IMAGES (~20 seconds if enabled)
        # Real: Pollinations.AI generation
        # =====================================
        generated_images = []
        if config.get('includeImages', False):
            image_count = config.get('imageCount', 3)
            
            yield f"data: {json.dumps(tracker.update_stage('images', 'working', 5, f'Preparing to generate {image_count} images...'))}\n\n"
            await asyncio.sleep(2)
            
            try:
                from tools.image_generator import ImageGenerator
                image_gen = ImageGenerator()
                
                yield f"data: {json.dumps(tracker.update_stage('images', 'working', 15, 'Analyzing content structure...'))}\n\n"
                await asyncio.sleep(3)
                
                yield f"data: {json.dumps(tracker.update_stage('images', 'working', 25, 'Extracting visual concepts...'))}\n\n"
                await asyncio.sleep(2)
                
                # Image 1
                yield f"data: {json.dumps(tracker.update_stage('images', 'working', 35, f'Generating image 1/{image_count}...'))}\n\n"
                
                # Run generation in thread pool
                loop = asyncio.get_event_loop()
                generated_images = await loop.run_in_executor(
                    None,
                    image_gen.generate_images_for_content,
                    mock_article,
                    tone,
                    image_count,
                    f"content_{job_id[:8]}"
                )
                
                # Image progress updates (even though generation is done)
                if image_count >= 2:
                    yield f"data: {json.dumps(tracker.update_stage('images', 'working', 55, f'Generating image 2/{image_count}...'))}\n\n"
                    await asyncio.sleep(3)
                
                if image_count >= 3:
                    yield f"data: {json.dumps(tracker.update_stage('images', 'working', 75, f'Generating image 3/{image_count}...'))}\n\n"
                    await asyncio.sleep(3)
                
                if generated_images:
                    yield f"data: {json.dumps(tracker.update_stage('images', 'working', 90, f'Successfully generated {len(generated_images)}/{image_count} images'))}\n\n"
                    await asyncio.sleep(2)
                    
                    yield f"data: {json.dumps(tracker.update_stage('images', 'working', 95, 'Embedding images in content...'))}\n\n"
                    mock_article = image_gen.embed_images_in_content(mock_article, generated_images)
                    await asyncio.sleep(2)
                    
                    yield f"data: {json.dumps(tracker.complete_stage('images'))}\n\n"
                else:
                    yield f"data: {json.dumps(tracker.update_stage('images', 'complete', 100, 'Completed (no images generated)'))}\n\n"
                
            except Exception as img_error:
                import traceback
                print(f"Image error: {traceback.format_exc()}")
                
                error_msg = f"Image generation issues: {str(img_error)[:80]}"
                yield f"data: {json.dumps(tracker.update_stage('images', 'complete', 100, error_msg))}\n\n"
        
        # Prepare image metadata
        image_metadata = []
        if generated_images:
            for img in generated_images:
                filename = Path(img['path']).name
                image_metadata.append({
                    'url': f"http://localhost:8000/images/{filename}",
                    'alt': img['alt_text'],
                    'caption': img['caption'],
                    'title': img['title'],
                    'concept': img['concept'],
                    'section': img.get('section', 'general')
                })
        
        actual_word_count = len(mock_article.split())
        
        # Final result
        result = {
            'type': 'complete',
            'jobId': job_id,
            'content': mock_article,
            'metadata': {
                'wordCount': actual_word_count,
                'targetWordCount': word_count,
                'qualityScore': 94,
                'keywords': config.get('keywords', [topic, 'technology', 'innovation', 'best practices']),
                'readabilityScore': 8.7,
                'seoScore': 91,
                'timestamp': datetime.now().isoformat(),
                'tone': tone,
                'generationTime': '163 seconds' if not image_metadata else '183 seconds',
                'topic': topic,
                'title': title,
                'images': image_metadata,
                'imageCount': len(generated_images)
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
    """Start content generation"""
    job_id = str(uuid.uuid4())
    
    config = {
        'topic': request.topic,
        'tone': request.tone,
        'word_count': request.wordCount,
        'keywords': request.keywords,
        'title': request.title or request.topic,
        'includeImages': request.includeImages,
        'imageCount': request.imageCount if request.includeImages else 0
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
    """Stream progress via SSE"""
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
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "activeJobs": len(active_jobs),
        "mode": "realistic_timing",
        "features": {
            "text_generation": "mock (~163s)",
            "image_generation": "real (~20s)",
            "total_time": "~163-183s"
        }
    }


@app.get("/api/jobs")
async def list_jobs():
    """List jobs"""
    return {"jobs": active_jobs, "total": len(active_jobs)}


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete job"""
    if job_id in active_jobs:
        del active_jobs[job_id]
        return {"message": "Job deleted", "jobId": job_id}
    raise HTTPException(status_code=404, detail="Job not found")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ContentForge API",
        "version": "1.0.0",
        "mode": "realistic_timing",
        "timing": {
            "research": "~40s",
            "writing": "~60s",
            "editing": "~35s",
            "seo": "~20s",
            "images": "~20s (if enabled)",
            "total": "~163-183s"
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "generate": "/api/generate",
            "stream": "/api/generate/{job_id}/stream",
            "images": "/images/{filename}"
        },
        "status": "✓ Server with REALISTIC timing (matches real backend)"
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 ContentForge FastAPI Server - REALISTIC TIMING")
    print("="*70)
    print("📡 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("💚 Health: http://localhost:8000/api/health")
    print()
    print("⏱️  REALISTIC TIMING (matches actual backend):")
    print("   • Research:  ~40s (Wikipedia + DuckDuckGo searches)")
    print("   • Writing:   ~60s (AI generating 1200-2000 words)")
    print("   • Editing:   ~35s (AI refining content)")
    print("   • SEO:       ~20s (keyword optimization)")
    print("   • Images:    ~20s (if enabled, real Pollinations.AI)")
    print("   • TOTAL:     ~163-183 seconds (2.7-3.0 minutes)")
    print()
    print("🎨 Images: REAL generation via Pollinations.AI")
    print("📝 Text: Mock data with realistic delays")
    print("="*70 + "\n")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )