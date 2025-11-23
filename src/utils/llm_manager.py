"""
LLM Manager with Intelligent Fallback System
Supports: Gemini → Groq → Ollama
"""

import os
import time
from typing import Optional, Dict, Any
from enum import Enum
import google.generativeai as genai
from groq import Groq
import ollama
from dotenv import load_dotenv

load_dotenv()

class LLMProvider(Enum):
    """Available LLM providers"""
    GEMINI = "gemini"
    GROQ = "groq"
    OLLAMA = "ollama"

class LLMManager:
    """
    Manages multiple LLM providers with intelligent fallback
    """
    
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
        
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.timeout = int(os.getenv("TIMEOUT_SECONDS", "30"))
        self.verbose = os.getenv("VERBOSE", "true").lower() == "true"
        
        # Usage tracking
        self.usage_stats = {
            "gemini": {"calls": 0, "failures": 0},
            "groq": {"calls": 0, "failures": 0},
            "ollama": {"calls": 0, "failures": 0}
        }
        
        # Initialize clients
        self._init_clients()
    
    def _init_clients(self):
        """Initialize all available LLM clients"""
        try:
            if self.gemini_key:
                genai.configure(api_key=self.gemini_key)
                self.gemini_client = genai.GenerativeModel(self.gemini_model)
                if self.verbose:
                    print("✅ Gemini initialized")
            else:
                self.gemini_client = None
                if self.verbose:
                    print("⚠️ Gemini API key not found")
        except Exception as e:
            self.gemini_client = None
            if self.verbose:
                print(f"❌ Gemini initialization failed: {e}")
        
        try:
            if self.groq_key:
                self.groq_client = Groq(api_key=self.groq_key)
                if self.verbose:
                    print("✅ Groq initialized")
            else:
                self.groq_client = None
                if self.verbose:
                    print("⚠️ Groq API key not found")
        except Exception as e:
            self.groq_client = None
            if self.verbose:
                print(f"❌ Groq initialization failed: {e}")
        
        try:
            # Test Ollama connection
            ollama.list()
            self.ollama_available = True
            if self.verbose:
                print("✅ Ollama initialized")
        except Exception as e:
            self.ollama_available = False
            if self.verbose:
                print(f"⚠️ Ollama not available: {e}")
    
    def generate(self, prompt: str, max_tokens: int = 2000, 
                 temperature: float = 0.7, provider: Optional[LLMProvider] = None) -> str:
        """
        Generate text with automatic fallback
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            provider: Force specific provider (optional)
        
        Returns:
            Generated text
        """
        if provider:
            return self._generate_with_provider(
                prompt, max_tokens, temperature, provider
            )
        
        # Try providers in order: Gemini → Groq → Ollama
        providers = [
            (LLMProvider.GEMINI, self.gemini_client),
            (LLMProvider.GROQ, self.groq_client),
            (LLMProvider.OLLAMA, self.ollama_available)
        ]
        
        for provider_enum, is_available in providers:
            if is_available:
                try:
                    result = self._generate_with_provider(
                        prompt, max_tokens, temperature, provider_enum
                    )
                    return result
                except Exception as e:
                    if self.verbose:
                        print(f"⚠️ {provider_enum.value} failed: {e}")
                    self.usage_stats[provider_enum.value]["failures"] += 1
                    continue
        
        raise Exception("All LLM providers failed. Check your API keys and Ollama installation.")
    
    def _generate_with_provider(self, prompt: str, max_tokens: int, 
                                temperature: float, provider: LLMProvider) -> str:
        """Generate text using a specific provider"""
        self.usage_stats[provider.value]["calls"] += 1
        
        if provider == LLMProvider.GEMINI:
            return self._generate_gemini(prompt, max_tokens, temperature)
        elif provider == LLMProvider.GROQ:
            return self._generate_groq(prompt, max_tokens, temperature)
        elif provider == LLMProvider.OLLAMA:
            return self._generate_ollama(prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _generate_gemini(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using Gemini"""
        if not self.gemini_client:
            raise Exception("Gemini client not initialized")
        
        if self.verbose:
            print("🔵 Using Gemini...")
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        
        response = self.gemini_client.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    def _generate_groq(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using Groq"""
        if not self.groq_client:
            raise Exception("Groq client not initialized")
        
        if self.verbose:
            print("🟠 Using Groq...")
        
        response = self.groq_client.chat.completions.create(
            model=self.groq_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    def _generate_ollama(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using Ollama (local)"""
        if not self.ollama_available:
            raise Exception("Ollama is not available")
        
        if self.verbose:
            print("🟢 Using Ollama (local)...")
        
        response = ollama.generate(
            model=self.ollama_model,
            prompt=prompt,
            options={
                "temperature": temperature,
                "num_predict": max_tokens
            }
        )
        
        return response['response']
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.usage_stats
    
    def print_usage_stats(self):
        """Print usage statistics"""
        print("\n📊 LLM Usage Statistics:")
        print("=" * 50)
        for provider, stats in self.usage_stats.items():
            total = stats["calls"]
            failures = stats["failures"]
            success_rate = ((total - failures) / total * 100) if total > 0 else 0
            print(f"{provider.upper()}: {total} calls | {failures} failures | {success_rate:.1f}% success")
        print("=" * 50)

# Singleton instance
_llm_manager = None

def get_llm_manager() -> LLMManager:
    """Get or create LLM manager instance"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager