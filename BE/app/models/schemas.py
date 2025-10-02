from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum

class ProcessingMode(str, Enum):
    SINGLE = "single"
    MULTI = "multi"

class PageContentRequest(BaseModel):
    content: str = Field(..., description="Text content of the webpage")
    layout: Dict[str, Any] = Field(..., description="Layout information of the webpage")
    url: str = Field(..., description="URL of the webpage")
    useMultiModel: bool = Field(False, description="Whether to use multi-model processing")

class MCQOption(BaseModel):
    text: str
    index: int

class MCQQuestion(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    question: str
    options: List[str]
    correct_option: int = Field(..., description="Index of correct option (0-3) or -1 if error/unknown")
    confidence: float
    reasoning: str
    model_responses: Optional[List[Dict[str, Any]]] = None

class ModelResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    model: str
    selected_option: int
    confidence: float
    reasoning: str

class MCQDetectionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    questions: List[MCQQuestion]
    processing_mode: ProcessingMode
    consensus: List[bool]
    total_questions: int
    cached: bool = False

class ExtractedMCQ(BaseModel):
    question: str
    options: List[str]
    question_index: int

class MCQExtractionResponse(BaseModel):
    mcqs: List[ExtractedMCQ]
    total_found: int

class AnswerRequest(BaseModel):
    question: str
    options: List[str]
    useMultiModel: bool = False

class AnswerResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    correct_option: int = Field(..., description="Index of correct option (0-3) or -1 if error/unknown")
    confidence: float
    reasoning: str
    model_responses: Optional[List[ModelResponse]] = None
    consensus: bool = False