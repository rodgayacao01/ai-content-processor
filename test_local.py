import asyncio
import os
from dotenv import load_dotenv
from src.models import ProcessingRequest, TaskType
from src.processor import AIContentProcessor

# Load environment variables
load_dotenv()

async def test_processor():
    print("Testing AI Content Processor locally...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env")
        return

    try:
        processor = AIContentProcessor(openai_api_key=api_key)
        
        text = "Artificial Intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals."
        
        print(f"\nInput text: {text[:50]}...")
        
        # Test Summarization
        print("\n1. Testing Summarization...")
        request = ProcessingRequest(
            text=text,
            tasks=[TaskType.SUMMARIZATION],
            options={"style": "concise"}
        )
        results = await processor.process_request(request)
        for res in results:
            print(f"Task: {res.task}")
            print(f"Status: {res.status}")
            print(f"Result: {res.result}")
            print(f"Time: {res.processing_time_ms:.2f}ms")

        # Test Sentiment
        print("\n2. Testing Sentiment Analysis...")
        request = ProcessingRequest(
            text=text,
            tasks=[TaskType.SENTIMENT]
        )
        results = await processor.process_request(request)
        for res in results:
            print(f"Task: {res.task}")
            print(f"Status: {res.status}")
            print(f"Result: {res.result}")
            print(f"Time: {res.processing_time_ms:.2f}ms")

    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_processor())
