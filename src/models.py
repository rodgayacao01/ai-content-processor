from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class TaskType(str, Enum):
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CLASSIFICATION = "classification"
    NER = "ner"
    SENTIMENT = "sentiment"
    NOTE_GENERATION = "note_generation"
    FORMATTING = "formatting"
    EMAIL_DRAFT = "email_draft"
    MARKETING_COPY = "marketing_copy"
    REPORT_SUMMARY = "report_summary"
    NORMALIZE_CONTENT = "normalize_content"

class ProcessingRequest(BaseModel):
    text: str = Field(..., description="Input text to process")
    tasks: List[TaskType] = Field(..., description="List of tasks to perform")
    options: Optional[Dict[str, Any]] = Field(default={}, description="Additional options for tasks (e.g., target_language)")

class TranslationResult(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    quality_score: Optional[float] = None

class ClassificationResult(BaseModel):
    categories: List[str]
    tags: List[str]

class Entity(BaseModel):
    text: str
    label: str
    description: Optional[str] = None

class NERResult(BaseModel):
    entities: List[Entity]
    relationships: List[Dict[str, Any]] = []

class SentimentResult(BaseModel):
    sentiment: str
    score: float
    emotion: str

class ContentGenerationResult(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

class ProcessingResult(BaseModel):
    task: TaskType
    result: Union[
        str, 
        TranslationResult, 
        ClassificationResult, 
        NERResult, 
        SentimentResult, 
        ContentGenerationResult,
        Dict[str, Any]
    ]
    processing_time_ms: float
    status: str = "success"
    error: Optional[str] = None

class BatchProcessingRequest(BaseModel):
    requests: List[ProcessingRequest]

class BatchProcessingResponse(BaseModel):
    results: List[List[ProcessingResult]]
    total_processing_time_ms: float
