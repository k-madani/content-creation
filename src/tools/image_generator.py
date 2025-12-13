"""
Image Generator Tool - Multimodal Integration
Generates contextually relevant images from text content
Uses free APIs: Pollinations.AI (primary) + Hugging Face (fallback)
"""

import os
import re
import requests
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import quote
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()


class ImageGenerator:
    """Generate images from text content without LLM calls"""
    
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.output_dir = Path("outputs/images")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Style mappings for different tones
        self.style_templates = {
            'professional': 'professional photography, clean, modern, high quality, corporate',
            'casual': 'lifestyle photography, natural lighting, warm, inviting, friendly',
            'technical': 'technical illustration, detailed, precise, schematic, diagram',
            'conversational': 'friendly, approachable, colorful, engaging, relatable',
            'formal': 'elegant, sophisticated, professional, refined, polished'
        }
    
    def generate_images_for_content(self, content: str, tone: str, 
                                    num_images: int = 3, 
                                    base_filename: str = "content") -> List[Dict]:
        """
        Main entry point: Generate images from content
        
        Args:
            content: The article content (markdown)
            tone: Writing tone (professional, casual, etc.)
            num_images: Number of images to generate
            base_filename: Base name for saved files
            
        Returns:
            List of dicts with image info: {'path', 'alt_text', 'concept', 'prompt'}
        """
        
        console.print("\n[cyan]🎨 Analyzing content for image generation...[/cyan]")
        
        # Extract visual concepts from content
        concepts = self._extract_visual_concepts(content, num_images)
        
        if not concepts:
            console.print("[yellow]⚠️  Could not extract concepts. Using generic prompts.[/yellow]")
            concepts = [{"text": "abstract concept", "context": "general"}]
        
        console.print(f"[dim]  → Found {len(concepts)} concept(s)[/dim]")
        
        # Generate images
        generated_images = []
        
        for i, concept in enumerate(concepts[:num_images], 1):
            console.print(f"\n[cyan]  Image {i}/{num_images}: {concept['text'][:50]}...[/cyan]")
            
            # Build prompt
            prompt = self._build_image_prompt(concept['text'], tone, concept.get('context', ''))
            console.print(f"[dim]    Prompt: {prompt[:80]}...[/dim]")
            
            # Generate image with fallback
            image_data = self._generate_with_fallback(prompt)
            
            if image_data:
                # Save image
                filename = f"{base_filename}_img{i}.png"
                filepath = self.output_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                # Generate alt text
                alt_text = self._generate_alt_text(concept['text'], tone)
                
                generated_images.append({
                    'path': str(filepath),
                    'relative_path': f"images/{filename}",
                    'alt_text': alt_text,
                    'concept': concept['text'],
                    'prompt': prompt
                })
                
                console.print(f"[green]    ✓ Generated: {filename}[/green]")
            else:
                console.print(f"[yellow]    ⚠️  Failed to generate image {i}[/yellow]")
        
        console.print(f"\n[green]✓ Generated {len(generated_images)}/{num_images} images[/green]\n")
        
        return generated_images
    
    def _extract_visual_concepts(self, content: str, num_needed: int) -> List[Dict]:
        """
        Extract visual concepts from content using pure Python
        No LLM calls - just regex and text analysis
        """
        
        concepts = []
        
        # 1. Extract title (H1) - Most important
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # Clean title
            title_clean = re.sub(r'[^\w\s-]', '', title).strip()
            concepts.append({
                'text': title_clean,
                'context': 'main_title',
                'priority': 1
            })
        
        # 2. Extract H2 headers - Section topics
        h2_headers = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        for header in h2_headers[:num_needed]:
            header_clean = re.sub(r'[^\w\s-]', '', header).strip()
            if len(header_clean) > 5:  # Skip very short headers
                concepts.append({
                    'text': header_clean,
                    'context': 'section_header',
                    'priority': 2
                })
        
        # 3. Extract from first paragraph (if needed)
        if len(concepts) < num_needed:
            first_para_match = re.search(r'^[^#\n].+?\n\n', content, re.MULTILINE | re.DOTALL)
            if first_para_match:
                first_para = first_para_match.group(0)
                # Extract key nouns (simple approach)
                words = re.findall(r'\b[A-Z][a-z]+\b', first_para)
                if words:
                    key_phrase = ' '.join(words[:3])  # First 3 capitalized words
                    concepts.append({
                        'text': key_phrase,
                        'context': 'introduction',
                        'priority': 3
                    })
        
        # Sort by priority and return
        concepts.sort(key=lambda x: x['priority'])
        
        return concepts
    
    def _build_image_prompt(self, concept: str, tone: str, context: str = '') -> str:
        """
        Build image generation prompt from concept
        Uses templates - no LLM needed
        """
        
        # Get style for tone
        style = self.style_templates.get(tone, self.style_templates['professional'])
        
        # Clean concept
        concept_clean = concept.strip()
        
        # Add context-specific modifiers
        context_modifiers = ""
        if context == 'main_title':
            context_modifiers = "hero image, featured, eye-catching"
        elif context == 'section_header':
            context_modifiers = "supporting illustration, contextual"
        
        # Build prompt
        prompt = f"{concept_clean}, {style}, {context_modifiers}, 8k, detailed, high resolution"
        
        # Clean up extra spaces
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        
        return prompt
    
    def _generate_with_fallback(self, prompt: str) -> Optional[bytes]:
        """
        Generate image with multi-tier fallback
        1. Pollinations.AI (free, unlimited)
        2. Hugging Face (free, requires key)
        3. Simplified prompt retry
        """
        
        # Tier 1: Pollinations.AI
        try:
            console.print("[dim]    → Trying Pollinations.AI...[/dim]")
            image_data = self._generate_pollinations(prompt)
            if image_data:
                console.print("[dim]    → Success with Pollinations[/dim]")
                return image_data
        except Exception as e:
            console.print(f"[dim]    → Pollinations failed: {str(e)[:50]}[/dim]")
        
        # Tier 2: Hugging Face (if API key available)
        if self.hf_api_key:
            try:
                console.print("[dim]    → Trying Hugging Face...[/dim]")
                image_data = self._generate_huggingface(prompt)
                if image_data:
                    console.print("[dim]    → Success with Hugging Face[/dim]")
                    return image_data
            except Exception as e:
                console.print(f"[dim]    → Hugging Face failed: {str(e)[:50]}[/dim]")
        
        # Tier 3: Retry with simplified prompt
        try:
            console.print("[dim]    → Retrying with simplified prompt...[/dim]")
            simple_prompt = self._simplify_prompt(prompt)
            console.print(f"[dim]    → Simplified: {simple_prompt[:60]}...[/dim]")
            
            image_data = self._generate_pollinations(simple_prompt)
            if image_data:
                console.print("[dim]    → Success with simplified prompt[/dim]")
                return image_data
        except Exception as e:
            console.print(f"[dim]    → Simplified retry failed: {str(e)[:50]}[/dim]")
        
        # All tiers failed
        return None
    
    def _generate_pollinations(self, prompt: str) -> Optional[bytes]:
        """
        Generate image using Pollinations.AI
        FREE, unlimited, no API key needed
        """
        
        # Encode prompt for URL
        encoded_prompt = quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        # Add parameters for better quality
        url += "?width=1024&height=1024&nologo=true"
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Pollinations API returned {response.status_code}")
    
    def _generate_huggingface(self, prompt: str) -> Optional[bytes]:
        """
        Generate image using Hugging Face Inference API
        FREE tier available, requires API key
        """
        
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Hugging Face API returned {response.status_code}")
    
    def _simplify_prompt(self, prompt: str) -> str:
        """Simplify prompt by removing complex descriptors"""
        
        # Extract main concept (first few words)
        words = prompt.split(',')
        if len(words) > 0:
            main_concept = words[0].strip()
            # Add basic quality descriptors
            return f"{main_concept}, high quality, detailed, professional"
        
        return prompt
    
    def _generate_alt_text(self, concept: str, tone: str) -> str:
        """Generate SEO-friendly alt text"""
        
        # Clean concept
        concept_clean = re.sub(r'[^\w\s-]', '', concept).strip()
        
        # Build alt text
        alt_text = f"AI-generated illustration of {concept_clean}"
        
        return alt_text
    
    def embed_images_in_content(self, content: str, images: List[Dict]) -> str:
        """
        Embed generated images into markdown content
        
        Strategy:
        - First image: After title (hero image)
        - Other images: After H2 headers
        """
        
        if not images:
            return content
        
        lines = content.split('\n')
        new_lines = []
        
        image_index = 0
        h2_count = 0
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Add first image after title (H1)
            if line.startswith('# ') and image_index == 0:
                new_lines.append('')
                img = images[image_index]
                new_lines.append(f"![{img['alt_text']}]({img['relative_path']})")
                new_lines.append(f"*{img['concept']}*")
                new_lines.append('')
                image_index += 1
            
            # Add remaining images after H2 headers
            elif line.startswith('## ') and image_index < len(images):
                h2_count += 1
                # Add image after every 1-2 H2s
                if h2_count % 2 == 0 or image_index == len(images) - 1:
                    # Add paragraph break if next line isn't empty
                    if i + 1 < len(lines) and lines[i + 1].strip():
                        new_lines.append('')
                    
                    img = images[image_index]
                    new_lines.append(f"![{img['alt_text']}]({img['relative_path']})")
                    new_lines.append(f"*{img['concept']}*")
                    new_lines.append('')
                    image_index += 1
        
        return '\n'.join(new_lines)


# Convenience function for direct import
def generate_images(content: str, tone: str, num_images: int = 3, 
                   base_filename: str = "content") -> List[Dict]:
    """
    Convenience function to generate images
    
    Returns:
        List of image info dicts
    """
    generator = ImageGenerator()
    return generator.generate_images_for_content(content, tone, num_images, base_filename)