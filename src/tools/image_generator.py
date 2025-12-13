"""
Image Generator Tool - VISUAL CONCEPTS ONLY (NO TEXT)
Focus: Relevant, high-quality visual imagery without text
"""

import os
import re
import requests
import time
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import quote
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()


class ImageGenerator:
    """Generate relevant, text-free images based on content context"""
    
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.output_dir = Path("outputs/images")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Visual style mappings - NO TEXT
        self.style_templates = {
            'professional': 'professional photography, modern office environment, clean aesthetic, corporate setting, natural lighting, high quality',
            'casual': 'lifestyle photography, friendly atmosphere, warm natural light, relaxed setting, candid moment, inviting',
            'technical': 'technology workspace, computer screens, modern equipment, sleek devices, blue lighting, futuristic',
            'conversational': 'friendly workspace, people collaborating, bright environment, modern interior, natural interaction',
            'formal': 'executive office, elegant interior, sophisticated lighting, premium materials, professional setting'
        }
        
        # Topic-to-visual mapping - HIGHLY VARIED CONCEPTS
        self.visual_concepts = {
            'technology': [
                'futuristic server room with glowing cables and network equipment',
                'abstract digital data streams and particles in space',
                'sleek modern tech office with multiple curved monitors'
            ],
            'business': [
                'skyscraper office with panoramic city view through glass walls',
                'abstract geometric shapes representing growth and strategy',
                'professional handshake with bokeh city lights background'
            ],
            'health': [
                'modern hospital corridor with natural light and plants',
                'medical technology devices and health monitoring equipment',
                'peaceful wellness spa with natural elements'
            ],
            'education': [
                'bright modern classroom with interactive digital boards',
                'abstract books floating in illuminated library space',
                'students collaborating with tablets and technology'
            ],
            'finance': [
                'abstract stock market graphs and financial data visualization',
                'luxury banking interior with marble and gold accents',
                'cityscape with financial district skyscrapers at sunset'
            ],
            'science': [
                'microscopic view of molecular structures and particles',
                'laboratory with glassware and colorful chemical reactions',
                'abstract scientific formulas and equations in space'
            ],
            'ai': [
                'glowing neural network connections in 3D space',
                'futuristic AI robot in modern laboratory environment',
                'abstract artificial intelligence brain visualization'
            ],
            'machine learning': [
                'massive data center with endless rows of servers',
                'abstract algorithm visualization with flowing data',
                'high-tech command center with multiple data displays'
            ],
            'data': [
                'colorful data visualization dashboard with charts and graphs',
                'abstract flowing data streams with particles and lights',
                'modern analytics workspace with multiple large screens'
            ],
            'cloud': [
                'enormous server farm from aerial perspective',
                'abstract cloud computing concept with connected nodes',
                'futuristic data center with blue atmospheric lighting'
            ],
            'marketing': [
                'vibrant creative agency with colorful brainstorming walls',
                'abstract social media icons and engagement visualization',
                'modern marketing team meeting with digital presentations'
            ],
            'design': [
                'minimalist design studio with clean white aesthetic',
                'colorful creative workspace with art supplies and tools',
                'abstract geometric design patterns and shapes'
            ],
            'development': [
                'dark coding environment with multiple monitors and code',
                'abstract programming symbols and binary code visualization',
                'collaborative developer workspace with standing desks'
            ],
            'application': [
                'modern software interface on multiple device screens',
                'abstract app icons floating in digital space',
                'user interacting with futuristic holographic interface'
            ]
        }
    
    def generate_images_for_content(self, content: str, tone: str, 
                                    num_images: int = 3, 
                                    base_filename: str = "content") -> List[Dict]:
        """
        Generate visually relevant images without text
        """
        
        console.print("\n[cyan]🎨 Analyzing content for visual concepts...[/cyan]")
        
        # Extract main topic
        topic = self._extract_main_topic(content)
        console.print(f"[dim]  → Main topic: {topic}[/dim]")
        
        # Generate visual concepts (not text-based)
        visual_scenes = self._create_visual_scenes(topic, content, num_images)
        
        if not visual_scenes:
            console.print("[yellow]⚠️  Using default visual concepts[/yellow]")
            visual_scenes = [
                {"scene": "modern professional workspace", "context": "general"},
                {"scene": "technology and innovation environment", "context": "general"},
                {"scene": "business meeting space", "context": "general"}
            ]
        
        console.print(f"[dim]  → Generated {len(visual_scenes)} visual scene(s)[/dim]")
        
        generated_images = []
        
        for i, scene_data in enumerate(visual_scenes[:num_images], 1):
            console.print(f"\n[cyan]  Image {i}/{num_images}: {scene_data['scene'][:60]}...[/cyan]")
            
            # Build visual prompt (NO TEXT GENERATION)
            prompt = self._build_visual_prompt(
                scene_data['scene'],
                topic,
                tone,
                scene_data.get('context', 'general')
            )
            console.print(f"[dim]    Prompt: {prompt[:80]}...[/dim]")
            
            # Add delay between generations
            if i > 1:
                console.print(f"[dim]    ⏳ Waiting 3 seconds...[/dim]")
                time.sleep(3)
            
            # Generate with retry
            image_data = self._generate_with_retry(prompt, max_attempts=3)
            
            if image_data:
                # Save image
                filename = f"{base_filename}_img{i}.png"
                filepath = self.output_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                # Generate metadata
                metadata = self._generate_image_metadata(
                    scene_data['scene'],
                    topic,
                    i
                )
                
                generated_images.append({
                    'path': str(filepath),
                    'relative_path': f"images/{filename}",
                    'alt_text': metadata['alt_text'],
                    'caption': metadata['caption'],
                    'title': metadata['title'],
                    'concept': scene_data['scene'],
                    'section': f"section_{i}",
                    'prompt': prompt,
                    'seo_filename': metadata['seo_filename']
                })
                
                console.print(f"[green]    ✓ Generated: {filename}[/green]")
            else:
                console.print(f"[yellow]    ⚠️  Failed to generate image {i}[/yellow]")
        
        console.print(f"\n[green]✓ Generated {len(generated_images)}/{num_images} visual images[/green]\n")
        
        return generated_images
    
    def _extract_main_topic(self, content: str) -> str:
        """Extract the main topic from content"""
        
        # Try to get from H1 title
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # Remove common filler words
            title = re.sub(r'\b(the|a|an|complete|guide|to|mastering|understanding|explained)\b', '', title, flags=re.IGNORECASE)
            title = re.sub(r'\s+', ' ', title).strip()
            
            # Get core keywords (2-3 words max)
            words = [w for w in title.split() if len(w) > 3][:3]
            topic = ' '.join(words) if words else title
            return topic.lower()
        
        return "technology"
    
    def _create_visual_scenes(self, topic: str, content: str, num_scenes: int) -> List[Dict]:
        """
        Create DISTINCT visual scene descriptions with maximum variety
        """
        
        scenes = []
        topic_lower = topic.lower()
        
        # Match topic to visual concepts
        matched_visuals = []
        for keyword, visuals in self.visual_concepts.items():
            if keyword in topic_lower:
                matched_visuals.extend(visuals)
        
        # If no matches, use varied generic scenes
        if not matched_visuals:
            matched_visuals = [
                'modern professional office space with glass walls',
                'abstract technology concept with circuit boards and electronics',
                'business meeting room with large windows and city view'
            ]
        
        # ENSURE VARIETY: Use different concepts for each image
        # Pad list if needed
        while len(matched_visuals) < num_scenes:
            matched_visuals.extend(matched_visuals[:num_scenes - len(matched_visuals)])
        
        # Create DISTINCTLY DIFFERENT scene types
        scene_types = [
            {
                'template': '{concept}, wide panoramic shot, expansive view, establishing scene',
                'context': 'hero',
                'description': 'wide overview',
                'style': 'cinematic, wide angle, dramatic perspective'
            },
            {
                'template': '{concept}, macro close-up, intricate details, shallow depth of field',
                'context': 'detail',
                'description': 'extreme close-up',
                'style': 'detailed, sharp focus, selective focus'
            },
            {
                'template': '{concept}, dramatic lighting, moody atmosphere, artistic composition',
                'context': 'atmosphere',
                'description': 'atmospheric mood',
                'style': 'cinematic lighting, dramatic shadows, artistic'
            }
        ]
        
        for i in range(min(num_scenes, len(scene_types))):
            # CRITICAL: Use DIFFERENT concept for each image
            base_concept = matched_visuals[i]
            scene_type = scene_types[i]
            
            # Build scene with distinct style
            scene_description = scene_type['template'].format(concept=base_concept)
            scene_description += f", {scene_type['style']}"
            
            scenes.append({
                'scene': scene_description,
                'context': scene_type['context'],
                'type': scene_type['description']
            })
        
        return scenes
    
    def _build_visual_prompt(self, scene: str, topic: str, tone: str, context: str) -> str:
        """
        Build comprehensive VISUAL prompt without text generation
        CRITICAL: Focus on environment, lighting, composition - NOT text
        """
        
        # Get style for tone
        style = self.style_templates.get(tone, self.style_templates['professional'])
        
        # Context-specific enhancements - MORE DRAMATIC DIFFERENCES
        context_details = {
            'hero': 'cinematic WIDE ANGLE composition, expansive panoramic view, establishing shot, DRAMATIC perspective, large scale',
            'detail': 'EXTREME CLOSE-UP, macro photography, intricate details, shallow depth of field, FOCUSED on subject, sharp foreground blur background',
            'atmosphere': 'DRAMATIC LIGHTING, moody cinematic atmosphere, artistic composition, strong shadows, AMBIENT lighting, film noir style'
        }
        
        context_detail = context_details.get(context, 'professional composition, balanced framing')
        
        # Build comprehensive visual prompt
        prompt = (
            f"{scene}, {context_detail}, {style}, "
            f"NO TEXT, NO WORDS, NO LETTERS, NO WRITING, pure visual imagery, "
            f"8k photography, professional quality, detailed, sharp focus"
        )
        
        # Clean up
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        prompt = re.sub(r',\s*,', ',', prompt)
        
        return prompt
    
    def _generate_image_metadata(self, scene: str, topic: str, image_num: int) -> Dict[str, str]:
        """Generate metadata for images"""
        
        # Alt text (accessibility)
        alt_text = f"Professional visual representing {topic} - image {image_num}"
        
        # Caption
        caption = f"Visual {image_num}: {topic.title()}"
        
        # Title
        title = f"{topic.title()} - Professional Illustration {image_num}"
        
        # SEO filename
        seo_filename = re.sub(r'\s+', '-', topic.lower())
        seo_filename = re.sub(r'[^\w-]', '', seo_filename)[:30]
        
        return {
            'alt_text': alt_text,
            'caption': caption,
            'title': title,
            'seo_filename': seo_filename
        }
    
    def _generate_with_retry(self, prompt: str, max_attempts: int = 3) -> Optional[bytes]:
        """Generate image with retry logic"""
        
        for attempt in range(1, max_attempts + 1):
            try:
                console.print(f"[dim]    → Attempt {attempt}/{max_attempts}...[/dim]")
                image_data = self._generate_pollinations(prompt)
                
                if image_data and len(image_data) > 10000:  # Valid image should be > 10KB
                    console.print(f"[dim]    → Success![/dim]")
                    return image_data
                else:
                    raise Exception("Image too small or invalid")
                    
            except Exception as e:
                console.print(f"[dim]    → Attempt {attempt} failed: {str(e)[:50]}[/dim]")
                
                if attempt < max_attempts:
                    wait_time = 2 ** attempt
                    console.print(f"[dim]    → Waiting {wait_time}s before retry...[/dim]")
                    time.sleep(wait_time)
        
        console.print(f"[red]    ✗ All {max_attempts} attempts failed[/red]")
        return None
    
    def _generate_pollinations(self, prompt: str) -> Optional[bytes]:
        """Generate image using Pollinations.AI with best settings"""
        
        encoded_prompt = quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        # Optimized parameters for quality
        params = {
            'width': '1024',
            'height': '1024',
            'nologo': 'true',
            'model': 'flux',
            'enhance': 'true',  # Enable enhancement
            'seed': str(int(time.time()))
        }
        
        url += '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
        
        # Increased timeout for better quality
        response = requests.get(url, timeout=90)
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Pollinations API returned {response.status_code}")
    
    def embed_images_in_content(self, content: str, images: List[Dict]) -> str:
        """Embed images strategically in content"""
        
        if not images:
            return content
        
        lines = content.split('\n')
        new_lines = []
        
        image_index = 0
        h2_count = 0
        
        # Calculate even spacing for images
        h2_positions = [i for i, line in enumerate(lines) if line.startswith('## ')]
        
        if h2_positions and len(images) > 1:
            spacing = max(1, len(h2_positions) // (len(images) - 1))
        else:
            spacing = 1
        
        # Insert images
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # HERO IMAGE: After H1 title
            if line.startswith('# ') and image_index == 0 and len(images) > 0:
                new_lines.append('')
                img = images[image_index]
                new_lines.append(f"![{img['alt_text']}]({img['relative_path']} \"{img['title']}\")")
                new_lines.append(f"*{img['caption']}*")
                new_lines.append('')
                image_index += 1
                console.print(f"[dim]  → Placed hero image after title[/dim]")
            
            # SECTION IMAGES: Evenly distributed after H2s
            elif line.startswith('## ') and image_index < len(images):
                h2_count += 1
                
                if h2_count % spacing == 0 or image_index == len(images) - 1:
                    new_lines.append('')
                    img = images[image_index]
                    new_lines.append(f"![{img['alt_text']}]({img['relative_path']} \"{img['title']}\")")
                    new_lines.append(f"*{img['caption']}*")
                    new_lines.append('')
                    
                    console.print(f"[dim]  → Placed image {image_index + 1} after section[/dim]")
                    image_index += 1
        
        return '\n'.join(new_lines)


# Convenience function
def generate_images(content: str, tone: str, num_images: int = 3, 
                   base_filename: str = "content") -> List[Dict]:
    """Convenience function to generate images"""
    generator = ImageGenerator()
    return generator.generate_images_for_content(content, tone, num_images, base_filename)
