"""
FastAPI web server - this creates REST API endpoints
so other apps can use our agent via HTTP requests
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import SchemeAgent
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Government Scheme Assistant API",
    description="AI-powered assistant to help find Indian government schemes",
    version="1.0.0"
)

# Enable CORS (so web browsers can access API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = SchemeAgent()

# Define request/response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# API Endpoints
@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "Government Scheme Assistant API",
        "version": "1.0.0"
    }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat endpoint
    Send a message, get AI response
    """
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get response from agent
        response = agent.get_response(request.message)
        
        return ChatResponse(response=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schemes")
def get_all_schemes():
    """Get list of all schemes in database"""
    try:
        schemes = agent.db.get_all_schemes()
        return {
            "total": len(schemes['ids']),
            "schemes": schemes['metadatas']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run server
if __name__ == "__main__":
    print("🚀 Starting API server...")
    print("📖 API docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)