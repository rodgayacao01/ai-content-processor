import asyncio
import os
import uvicorn
from dotenv import load_dotenv
from apify import Actor

# Load environment variables from .env file
load_dotenv()

from src.models import ProcessingRequest, TaskType, BatchProcessingRequest
from src.processor import AIContentProcessor
from src.server import app

async def main():
    async with Actor:
        # Get input
        actor_input = await Actor.get_input() or {}
        
        openai_api_key = actor_input.get('openai_api_key')
        if openai_api_key:
            os.environ['OPENAI_API_KEY'] = openai_api_key
        
        standby = actor_input.get('standby', False)
        
        if standby:
            Actor.log.info("Starting in Standby Mode (Web Server)...")
            # In Apify, the container port is usually specified by ACTOR_WEB_SERVER_PORT
            port = int(os.getenv('ACTOR_WEB_SERVER_PORT', 8000))
            config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
            server = uvicorn.Server(config)
            await server.serve()
        else:
            Actor.log.info("Starting in Run-Once Mode...")
            input_text = actor_input.get('input_text')
            tasks = actor_input.get('tasks', [])
            
            if not input_text:
                Actor.log.error("No input text provided. Exiting.")
                await Actor.fail(status_message="No input text provided")
                return

            # Convert string tasks to TaskType enum
            task_enums = []
            for t in tasks:
                try:
                    task_enums.append(TaskType(t))
                except ValueError:
                    Actor.log.warning(f"Warning: Ignoring invalid task '{t}'")
            
            if not task_enums:
                task_enums = [TaskType.SUMMARIZATION]

            request = ProcessingRequest(text=input_text, tasks=task_enums)
            
            try:
                processor = AIContentProcessor()
                results = await processor.process_request(request)
                
                # Serialize results for storage
                serialized_results = []
                for res in results:
                    serialized_results.append(res.model_dump())
                
                # Push results to dataset
                await Actor.push_data(serialized_results)
                Actor.log.info("Results pushed to dataset.")
                    
            except Exception as e:
                Actor.log.error(f"Error processing request: {e}")
                await Actor.fail(status_message=f"Error processing request: {e}")

if __name__ == "__main__":
    asyncio.run(main())
