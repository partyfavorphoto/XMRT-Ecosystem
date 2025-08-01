# launcher.py - The Production Web Server & API for Eliza

import os
import asyncio
import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse # We need this to serve our HTML page
from pydantic import BaseModel # For creating structured API requests
import uvicorn

# Import your main service class from main.py
from main import AIAutomationService

# --- Basic Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Eliza AI Automation Service",
    version="3.3.1", # Version bump for the fix!
    description="Live Production Instance of Eliza's Core Agent System"
)

# --- Pydantic Models for our Chat API ---
class ChatMessage(BaseModel):
    message: str

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """
    This is the root endpoint. It reads and returns your index.html file,
    serving the beautiful chat interface to the browser.
    """
    try:
        # This assumes index.html is in a 'static' subfolder
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        logger.error("FATAL: static/index.html not found! The chat interface cannot be served.")
        return HTMLResponse(content="<h1>Error 500: Interface file not found.</h1><p>Server is running, but the admin needs to add the index.html file.</p>", status_code=500)

@app.post("/api/chat")
async def handle_chat(chat_message: ChatMessage):
    """
    This is the dedicated endpoint for handling chat messages.
    The JavaScript from our HTML page will send requests here.
    """
    user_message = chat_message.message
    logger.info(f"Received chat message: {user_message}")
    
    # Placeholder logic for smart responses
    if "governance" in user_message.lower():
        response = "Of course. I am analyzing current governance proposals. Proposal #125 seems to have low community sentiment. Would you like a detailed report?"
    elif "treasury" in user_message.lower():
        response = "Accessing treasury data. The current risk-adjusted yield is 4.7%. I've identified an opportunity to reallocate 5% of assets for a potential 0.5% APY increase. Shall I draft the proposal?"
    elif "hello" in user_message.lower():
        response = "Hello. I am Eliza, the autonomous AI for the XMRT DAO. All systems are operational. How may I assist you?"
    else:
        response = f"I am processing your request: '{user_message}'. My agents are standing by to assist with governance, treasury, and community operations."

    return {"response": response}

@app.get("/health", status_code=200)
async def health_check():
    """The health check for Render remains the same."""
    return {"status": "healthy", "message": "Eliza Agent Service is online and responsive."}

# --- FastAPI Startup Event ---
@app.on_event("startup")
async def on_startup():
    """When the server starts, it still launches your agent logic in the background."""
    logger.info("Application startup: Launching background agent service.")
    service = AIAutomationService()
    asyncio.create_task(service.start_automation())
    logger.info("✅ Background agent service has been scheduled to run.")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("launcher:app", host="0.0.0.0", port=port, reload=True)
