# launcher.py
import os
import asyncio
import logging
from fastapi import FastAPI
import uvicorn

# Import your main service class from your existing main.py
# This assumes your main.py file contains the AIAutomationService class
try:
    from main import AIAutomationService
except ImportError as e:
    logging.error(f"Could not import AIAutomationService from main.py: {e}")
    # Exit if the core class can't be found
    exit(1)

# --- Basic Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# This is the FastAPI application that Render will see.
app = FastAPI(
    title="Eliza AI Automation Service",
    version="3.3.0",
    description="Live Production Instance of Eliza's Core Agent System"
)

# --- Health Check Endpoint for Render ---
# This is the single most important endpoint. Render pings this to see if the service is alive.
@app.get("/health", status_code=200)
async def health_check():
    return {"status": "healthy", "message": "Eliza Agent Service is online and ready."}

@app.get("/")
async def root():
    return {"service": "Eliza AI Automation Service", "status": "online"}

# --- FastAPI Startup Event ---
@app.on_event("startup")
async def on_startup():
    """When the server starts, create a background task for the agent logic."""
    logger.info("Application startup: Launching background agent service.")
    
    # Create an instance of your main service class
    service = AIAutomationService()
    
    # This crucial line starts your main loop without blocking the web server.
    asyncio.create_task(service.start_automation())
    
    logger.info("✅ Background service has been scheduled to run.")

# This part allows you to run the file directly for local testing.
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    logger.info(f"Starting development server on http://0.0.0.0:{port}")
    uvicorn.run("launcher:app", host="0.0.0.0", port=port, reload=True)
