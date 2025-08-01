# launcher.py
import os
import asyncio
import logging
from fastapi import FastAPI
import uvicorn

# Import your main service class from your existing main.py
from main import AIAutomationService

# --- Basic Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# This is the FastAPI web server application
app = FastAPI(
    title="Eliza AI Automation Service",
    version="3.3.0",
    description="Production-Ready Autonomous Agent System"
)

# --- Health Check Endpoint for Render ---
# This is CRUCIAL. Render will ping this URL to see if your service is alive.
@app.get("/health", status_code=200)
async def health_check():
    return {"status": "healthy", "message": "Eliza Agent Service is online and healthy."}

@app.get("/")
async def root():
    """A root endpoint to confirm the service is accessible via a browser."""
    # We can add a call to your service's status method here later
    return {"service": "Eliza AI Automation Service", "status": "online"}

# --- FastAPI Startup Event ---
# This tells the web server what to do right after it starts.
@app.on_event("startup")
async def on_startup():
    """When the server starts, create a background task for the agent logic."""
    logger.info("Application startup: Launching background agent service.")
    
    # Create an instance of your main service class
    service = AIAutomationService()
    
    # This line is key: it starts your main loop without blocking the web server.
    asyncio.create_task(service.start_automation())
    
    logger.info("✅ Background service has been scheduled to run.")

# This part allows you to run the file directly for local testing.
# Render will use the 'startCommand' from your render.yaml instead.
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    logger.info(f"Starting development server on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
