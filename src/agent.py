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
            self.groq_api_key = os.getenv("GROQ_API_KEY", "")
            self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
            self.model = "llama-3.1-70b-versatile"
        else:
            self.ollama_url = "http://localhost:11434/api/generate"
            self.model = "llama3.2"
        
    def query_llm(self, prompt):
        """Send prompt to LLM (Groq or Ollama)"""
        
        if self.use_groq:
            return self.query_groq(prompt)
        else:
            return self.query_ollama(prompt)
    
    def query_groq(self, prompt):
        """Query Groq API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(self.groq_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error connecting to AI: {str(e)}"
    
    def query_ollama(self, prompt):
        """Send prompt to Ollama (local)"""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"
    
    def get_response(self, user_message):
        """Main function to process user message and return response"""
        
        # Step 1: Search database for relevant schemes
        relevant_schemes = self.db.search_schemes(user_message, n_results=3)
        
        # Step 2: Create context from schemes
        schemes_context = "\n\n".join([
            f"Scheme: {s['name']}\n"
            f"Description: {s['description']}\n"
            f"Eligibility: {s['eligibility']}\n"
            f"Benefits: {s['benefits']}\n"
            f"Documents: {s['documents_required']}\n"
            f"How to Apply: {s['how_to_apply']}\n"
            f"Website: {s['website']}"
            for s in relevant_schemes
        ])
        
        # Step 3: Create prompt for LLM
        system_prompt = """You are a helpful government scheme assistant for India. 
        Your job is to help people find and understand government schemes they're eligible for.
        
        Be friendly, clear, and concise. Use simple language.
        Always mention the scheme website so users can apply.
        If someone asks about eligibility, explain clearly what they need.
        """
        
        prompt = f"""{system_prompt}

Based on these government schemes:

{schemes_context}

User Question: {user_message}

Provide a helpful response about the most relevant scheme(s). Include:
1. Which scheme(s) match their needs
2. Key benefits
3. Basic eligibility
4. How to apply
5. Website link

Response:"""
        
        # Step 4: Get AI response
        response = self.query_llm(prompt)
        
        return response