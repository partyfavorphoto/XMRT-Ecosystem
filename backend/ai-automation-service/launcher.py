# launcher.py - The Production Web Server for Eliza's Agent Core
import os
import asyncio
import logging
from fastapi import FastAPI
import uvicorn

# This now imports from your refactored main.py
from main import AIAutomationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Eliza AI Automation Service", version="3.3.0")

@app.get("/health", status_code=200)
async def health_check():
    return {"status": "healthy", "message": "Eliza Agent Service is online."}

@app.on_event("startup")
async def on_startup():
    logger.info("Application startup: Launching background agent service.")
    service = AIAutomationService()
    asyncio.create_task(service.start_automation())
    logger.info("✅ Background agent service has been scheduled.")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("launcher:app", host="0.0.0.0", port=port, reload=True)
