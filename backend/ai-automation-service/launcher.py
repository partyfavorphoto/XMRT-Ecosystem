# launcher.py - The Production Web Server for Eliza's Agent Core

import os
import asyncio
import logging
from fastapi import FastAPI
import uvicorn

# Import your main service class from your existing main script
# We'll rename your 'advanced_eliza_orchestrator.py' to 'eliza_service.py'
try:
    from eliza_service import AIAutomationService
except ImportError:
    logging.error("CRITICAL: Could not import AIAutomationService from eliza_service.py. Make sure the file and class exist.")
    exit(1)

# --- Basic Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# This is the FastAPI web application that Render will talk to.
app = FastAPI(
    title="Eliza AI Orchestrator",
    version="3.3.0",
    description="Live Production Instance of Eliza's Autonomous Agent System"
)

# --- Health Check Endpoint for Render ---
# This is the single most important endpoint. Render pings this to confirm the service is healthy.
@app.get("/health", status_code=200)
async def health_check():
    # We can add more detailed checks here later (e.g., check Redis, DB)
    return {"status": "healthy", "message": "Eliza Orchestrator is online and responsive."}

@app.get("/")
async def root():
    return {"service": "Eliza AI", "status": "online"}

# --- FastAPI Startup Event ---
@app.on_event("startup")
async def on_startup():
    """When the server starts, create a background task for the agent logic."""
    logger.info("Application startup: Launching background agent service.")
    
    # Create an instance of your main service class
    service = AIAutomationService()
    
    # This crucial line starts your main agent loop without blocking the web server.
    asyncio.create_task(service.start_automation())
    
    logger.info("✅ Background agent service has been scheduled to run.")

# This part allows you to run the file directly for local testing.
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    logger.info(f"Starting development server on http://0.0.0.0:{port}")
    uvicorn.run("launcher:app", host="0.0.0.0", port=port, reload=True)