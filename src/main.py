import asyncio
import os
import uvicorn
from dotenv import load_dotenv
from apify_client import ApifyClient

# Load environment variables from .env file
load_dotenv()

from src.models import ProcessingRequest, TaskType, BatchProcessingRequest
from src.processor import AIContentProcessor
from src.server import app

async def main():
    # Initialize Apify Client
    client = ApifyClient()
    
    # Get input
    actor_input = client.key_value_store(os.getenv('APIFY_DEFAULT_KEY_VALUE_STORE_ID')).get_record('INPUT').get('value') or {}
    
    openai_api_key = actor_input.get('openai_api_key')
    if openai_api_key:
        os.environ['OPENAI_API_KEY'] = openai_api_key
    
    standby = actor_input.get('standby', False)
    
    if standby:
        print("Starting in Standby Mode (Web Server)...")
        # In Apify, the container port is usually specified by ACTOR_WEB_SERVER_PORT
        port = int(os.getenv('ACTOR_WEB_SERVER_PORT', 8000))
        config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    else:
        print("Starting in Run-Once Mode...")
        input_text = actor_input.get('input_text')
        tasks = actor_input.get('tasks', [])
        
        if not input_text:
            print("No input text provided. Exiting.")
            return

        # Convert string tasks to TaskType enum
        task_enums = []
        for t in tasks:
            try:
                task_enums.append(TaskType(t))
            except ValueError:
                print(f"Warning: Ignoring invalid task '{t}'")
        
        if not task_enums:
            task_enums = [TaskType.SUMMARIZATION]

        request = ProcessingRequest(text=input_text, tasks=task_enums)
        
        try:
            processor = AIContentProcessor()
            results = await processor.process_request(request)
            
            # Push results to dataset
            dataset_id = os.getenv('APIFY_DEFAULT_DATASET_ID')
            if dataset_id:
                # Serialize results for storage
                serialized_results = []
                for res in results:
                    serialized_results.append(res.model_dump())
                
                client.dataset(dataset_id).push_items(serialized_results)
                print("Results pushed to dataset.")
            else:
                print("Results:", results)
                
        except Exception as e:
            print(f"Error processing request: {e}")

if __name__ == "__main__":
    asyncio.run(main())
