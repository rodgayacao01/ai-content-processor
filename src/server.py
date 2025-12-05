from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from src.models import ProcessingRequest, BatchProcessingRequest, BatchProcessingResponse
from src.processor import AIContentProcessor
from src.utils import logger
import os
import asyncio
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Content Processor API", version="1.0")

# Security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        # In Apify Actor context, we might not enforce this if authenticated via Apify Proxy
        # But for standalone, it's good practice.
        pass 
    return api_key_header

def get_processor():
    try:
        return AIContentProcessor()
    except ValueError as e:
        logger.error(f"Failed to initialize processor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    logger.info("Health check endpoint called")
    return {"status": "ok", "message": "AI Content Processor is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/process", response_model=BatchProcessingResponse)
async def process_content(
    request: BatchProcessingRequest, 
    processor: AIContentProcessor = Depends(get_processor),
    api_key: str = Depends(get_api_key)
):
    start_time = time.time()
    tasks = []
    for req in request.requests:
        tasks.append(processor.process_request(req))
    
    results = await asyncio.gather(*tasks)
    
    total_time = (time.time() - start_time) * 1000
    return BatchProcessingResponse(results=results, total_processing_time_ms=total_time)
