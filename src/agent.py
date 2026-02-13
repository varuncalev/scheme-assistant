import os
import requests
import json
from database import SchemeDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SchemeAgent:
    def __init__(self):
        """Initialize the agent"""
        self.db = SchemeDatabase()
        
        # Use Groq for production, Ollama for local
        self.use_groq = os.getenv("USE_GROQ", "false").lower() == "true"
        
        if self.use_groq:
            self.groq_api_key = os.getenv("GROQ_API_KEY", "")  # ✅ From environment
            if not self.groq_api_key:
                raise ValueError("GROQ_API_KEY environment variable not set!")
            self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
            self.model = "llama-3.1-70b-versatile"
        else:
            self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
            self.model = "llama3.2"
        
    # ... rest of your code ...