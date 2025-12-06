# AI Content Processor Actor

This Apify Actor provides a comprehensive suite of AI-powered text processing and content generation tools. It is designed to be high-availability, scalable, and easy to integrate via REST API or as a standalone batch processor.

## How It Works

The **AI Content Processor** leverages OpenAI's **GPT-4o-mini** model via LangChain to perform complex NLP tasks and content generation efficiently. It operates in two distinct modes:

### 1. Run-Once Mode (Batch Processing)
In this mode, the Actor reads input configuration, processes the text according to the specified tasks, pushes the results to the Apify Dataset, and then exits. This is ideal for:
- Processing a single document or a batch of text from the Apify Console.
- Scheduled jobs (e.g., summarizing daily news).
- Integration with other Actors in a workflow.

**Workflow:**
1. **Input**: Receives `input_text` and `tasks` from the input configuration.
2. **Process**: The `AIContentProcessor` (powered by LangChain) executes each task sequentially or in parallel.
3. **Output**: Results are validated against schemas and pushed to the default Apify Dataset.

### 2. Standby Mode (Web Server)
In this mode, the Actor starts a high-performance **FastAPI** server and listens for HTTP requests. This keeps the container warm, allowing for instant responses without cold-start delays. This is ideal for:
- Real-time applications (e.g., a chatbot backend).
- High-volume processing where you want to avoid spinning up a new container for every request.
- Integrating via REST API with external systems.

**Workflow:**
1. **Start**: The Actor starts a web server on the port defined by `ACTOR_WEB_SERVER_PORT`.
2. **Request**: Clients send `POST /process` requests with a JSON body containing a batch of texts and tasks.
3. **Response**: The server processes the requests asynchronously and returns the results immediately.

---

## Pricing

This Actor is priced based on the **Pay-per-event** model, ensuring you only pay for what you use.

- **Price**: **$0.50 per 1,000 processed results**.
- **Minimum**: No minimum usage.
- **Compute**: Included in the price.
- **AI Costs**: You provide your own OpenAI API Key, giving you full control over your model usage and costs.

## Features

### Core NLP Processing
- **Summarization**: Extractive and abstractive summarization with style controls.
- **Translation**: Multi-language translation with quality assessment.
- **Classification**: Multi-label content categorization and tagging.
- **Named Entity Recognition (NER)**: Extracts entities and relationships.
- **Sentiment Analysis**: Analyzes sentiment score and emotion.
- **Note Generation**: Converts unstructured text into structured notes.
- **Formatting**: Standardizes text format and normalization.

### Content Generation
- **Email Drafting**: Generates professional email drafts.
- **Marketing Copy**: Creates variations of marketing copy.
- **Report Summaries**: Generates executive-level report summaries.
- **Content Normalization**: Unifies tone and style.

---

## Usage

### Input Schema

The Actor accepts the following input:

```json
{
    "openai_api_key": "YOUR_OPENAI_API_KEY",
    "input_text": "Text to process...",
    "tasks": ["summarization", "sentiment"],
    "standby": false
}
```

- `openai_api_key`: Your OpenAI API Key (required).
- `input_text`: The raw text to process (for Run-Once mode).
- `tasks`: A list of tasks to perform.
- `standby`: If `true`, runs as a long-running web server (API mode).

### Output (Run-Once Mode)

The results are stored in the default Apify Dataset.

```json
[
    {
        "task": "summarization",
        "result": "Summary text...",
        "processing_time_ms": 1200,
        "status": "success"
    },
    {
        "task": "sentiment",
        "result": {
            "sentiment": "positive",
            "score": 0.8,
            "emotion": "joy"
        },
        "processing_time_ms": 500,
        "status": "success"
    }
]
```

---

## API Integration (Standby Mode)

When running in `standby` mode, the Actor exposes a REST API.

### Endpoints

- `POST /process`: Process a batch of content.
- `GET /health`: Health check.

#### Request Body (`/process`)

```json
{
  "requests": [
    {
      "text": "Content to process",
      "tasks": ["ner", "classification"],
      "options": {
        "target_language": "Spanish"
      }
    }
  ]
}
```

---

## Development

### Local Setup

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your environment:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

### Running Locally

**Run Once Mode:**
```bash
# Mock Apify input (or rely on defaults/env vars)
export APIFY_DEFAULT_KEY_VALUE_STORE_ID="local"
python -m src.main
```

**Server Mode:**
```bash
uvicorn src.server:app --reload
```

## Deployment

This Actor is containerized and ready for deployment on the Apify Platform.

1. Push the code to Apify.
2. Build the Actor.
3. Run via API or Scheduler.
