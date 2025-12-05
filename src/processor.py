import time
import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from src.models import (
    TaskType, 
    ProcessingRequest, 
    ProcessingResult, 
    TranslationResult,
    ClassificationResult,
    NERResult,
    SentimentResult,
    ContentGenerationResult,
    Entity
)

from src.utils import logger, PerformanceMonitor

class AIContentProcessor:
    def __init__(self, openai_api_key: str = None):
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API Key is required")
        
        self.llm = ChatOpenAI(
            api_key=self.api_key, 
            model="gpt-4o-mini", # Using a cost-effective and capable model
            temperature=0.1 # Low temperature for consistent results
        )

    async def process_request(self, request: ProcessingRequest) -> List[ProcessingResult]:
        results = []
        for task in request.tasks:
            start_time = time.time()
            status = "success"
            error_msg = None
            result_data = None
            
            try:
                logger.info(f"Starting task: {task}")
                if task == TaskType.SUMMARIZATION:
                    result_data = await self._summarize(request.text, request.options)
                elif task == TaskType.TRANSLATION:
                    result_data = await self._translate(request.text, request.options)
                elif task == TaskType.CLASSIFICATION:
                    result_data = await self._classify(request.text, request.options)
                elif task == TaskType.NER:
                    result_data = await self._extract_entities(request.text, request.options)
                elif task == TaskType.SENTIMENT:
                    result_data = await self._analyze_sentiment(request.text, request.options)
                elif task == TaskType.NOTE_GENERATION:
                    result_data = await self._generate_notes(request.text, request.options)
                elif task == TaskType.FORMATTING:
                    result_data = await self._format_text(request.text, request.options)
                elif task in [TaskType.EMAIL_DRAFT, TaskType.MARKETING_COPY, TaskType.REPORT_SUMMARY, TaskType.NORMALIZE_CONTENT]:
                     result_data = await self._generate_content(task, request.text, request.options)
                else:
                    raise ValueError(f"Unsupported task: {task}")
                
            except Exception as e:
                status = "error"
                error_msg = str(e)
                logger.error(f"Error processing task {task}: {e}")
                result_data = str(e)

            processing_time = (time.time() - start_time) * 1000
            PerformanceMonitor.log_request(task, processing_time, status, error_msg)
            
            results.append(ProcessingResult(
                task=task,
                result=result_data,
                processing_time_ms=processing_time,
                status=status,
                error=error_msg
            ))
        return results

    async def _summarize(self, text: str, options: Dict[str, Any]) -> str:
        style = options.get("style", "concise")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that summarizes text."),
            ("user", f"Please provide a {{style}} summary of the following text:\n\n{{text}}")
        ])
        chain = prompt | self.llm | StrOutputParser()
        return await chain.ainvoke({"text": text, "style": style})

    async def _translate(self, text: str, options: Dict[str, Any]) -> TranslationResult:
        target_lang = options.get("target_language", "English")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a professional translator."),
            ("user", "Translate the following text to {target_language}. Return a JSON object with 'translated_text', 'source_language', 'target_language', and 'quality_score' (0.0-1.0). Text:\n\n{text}")
        ])
        parser = JsonOutputParser(pydantic_object=TranslationResult)
        chain = prompt | self.llm | parser
        return await chain.ainvoke({"text": text, "target_language": target_lang})

    async def _classify(self, text: str, options: Dict[str, Any]) -> ClassificationResult:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a content classifier."),
            ("user", "Classify the following text into categories and tags. Return JSON with 'categories' (list of strings) and 'tags' (list of strings). Text:\n\n{text}")
        ])
        parser = JsonOutputParser(pydantic_object=ClassificationResult)
        chain = prompt | self.llm | parser
        return await chain.ainvoke({"text": text})

    async def _extract_entities(self, text: str, options: Dict[str, Any]) -> NERResult:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert in Named Entity Recognition."),
            ("user", "Extract named entities and their relationships from the text. Return JSON with 'entities' (list of objects with text, label, description) and 'relationships' (list of objects). Text:\n\n{text}")
        ])
        parser = JsonOutputParser(pydantic_object=NERResult)
        chain = prompt | self.llm | parser
        return await chain.ainvoke({"text": text})

    async def _analyze_sentiment(self, text: str, options: Dict[str, Any]) -> SentimentResult:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a sentiment analysis expert."),
            ("user", "Analyze the sentiment and emotion of the text. Return JSON with 'sentiment' (positive, negative, neutral), 'score' (-1.0 to 1.0), and 'emotion' (e.g., joy, anger). Text:\n\n{text}")
        ])
        parser = JsonOutputParser(pydantic_object=SentimentResult)
        chain = prompt | self.llm | parser
        return await chain.ainvoke({"text": text})
    
    async def _generate_notes(self, text: str, options: Dict[str, Any]) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an assistant that converts unstructured text into structured notes."),
            ("user", "Convert the following text into structured bullet points and key takeaways:\n\n{text}")
        ])
        chain = prompt | self.llm | StrOutputParser()
        return await chain.ainvoke({"text": text})

    async def _format_text(self, text: str, options: Dict[str, Any]) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a text formatting expert. Normalize whitespace, fix punctuation, and ensure consistent formatting."),
            ("user", "Format the following text:\n\n{text}")
        ])
        chain = prompt | self.llm | StrOutputParser()
        return await chain.ainvoke({"text": text})

    async def _generate_content(self, task: TaskType, text: str, options: Dict[str, Any]) -> ContentGenerationResult:
        system_prompts = {
            TaskType.EMAIL_DRAFT: "You are an expert email composer. Draft an email based on the context.",
            TaskType.MARKETING_COPY: "You are a marketing copywriter. Create marketing copy variations based on the input.",
            TaskType.REPORT_SUMMARY: "You are an executive assistant. Create an executive report summary.",
            TaskType.NORMALIZE_CONTENT: "You are a content editor. Normalize the tone and style of the content to be professional and consistent."
        }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompts.get(task, "You are a helpful content assistant.")),
            ("user", "Process the following input according to your role. Return JSON with 'content' (the generated text) and 'metadata' (any relevant info like tone used, etc.). Input:\n\n{text}")
        ])
        parser = JsonOutputParser(pydantic_object=ContentGenerationResult)
        chain = prompt | self.llm | parser
        return await chain.ainvoke({"text": text})
