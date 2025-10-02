from fastapi import APIRouter, HTTPException, Depends
from typing import List
import asyncio

from app.models.schemas import (
    PageContentRequest, 
    MCQDetectionResponse, 
    MCQQuestion,
    ProcessingMode,
    AnswerRequest,
    AnswerResponse
)
from app.services.ai_service import AIService
from app.services.redis_service import RedisService

router = APIRouter()

async def get_ai_service():
    """Dependency to get AI service instance"""
    return AIService()

async def get_redis_service():
    """Dependency to get Redis service instance"""
    return RedisService()

@router.post("/detect-mcqs", response_model=MCQDetectionResponse)
async def detect_mcqs(
    request: PageContentRequest,
    ai_service: AIService = Depends(get_ai_service),
    redis_service: RedisService = Depends(get_redis_service)
):
    """
    Detect and solve MCQs from webpage content
    
    This endpoint:
    1. Extracts MCQs from the webpage content
    2. Processes each question through AI model(s)
    3. Returns answers with reasoning and consensus info
    """
    try:
        processing_mode = ProcessingMode.MULTI if request.useMultiModel else ProcessingMode.SINGLE
        
        # Check cache for full page analysis first
        cached_result = await redis_service.get_cached_page_analysis(
            request.url, 
            request.content
        )
        
        if cached_result:
            cached_result["cached"] = True
            return MCQDetectionResponse(**cached_result)
        
        # Extract MCQs from content
        print(f"Extracting MCQs from content (length: {len(request.content)})")
        
        # Check cache for MCQ extraction
        cached_mcqs = await redis_service.get_cached_mcq_extraction(request.content)
        
        if cached_mcqs:
            extracted_mcqs = cached_mcqs
            print(f"Using cached MCQ extraction: {len(extracted_mcqs)} questions")
        else:
            extracted_mcqs = await ai_service.extract_mcqs_from_content(
                request.content, 
                request.layout
            )
            print(f"Extracted {len(extracted_mcqs)} MCQs from content")
            
            # Cache the extraction
            await redis_service.cache_mcq_extraction(request.content, extracted_mcqs)
        
        if not extracted_mcqs:
            return MCQDetectionResponse(
                questions=[],
                processing_mode=processing_mode,
                consensus=[],
                total_questions=0,
                cached=False
            )
        
        # Process each MCQ through AI models
        processed_questions = []
        consensus_results = []
        
        for mcq in extracted_mcqs:
            question_text = mcq.get("question", "")
            options = mcq.get("options", [])
            
            if not question_text or not options:
                continue
            
            # Check cache for this specific question
            cached_answer = await redis_service.get_cached_mcq_answer(question_text, options)
            
            if cached_answer:
                print(f"Using cached answer for question: {question_text[:50]}...")
                
                if request.useMultiModel:
                    mcq_question = MCQQuestion(
                        question=question_text,
                        options=options,
                        correct_option=cached_answer.get("correct_option", 0),
                        confidence=cached_answer.get("confidence", 0),
                        reasoning=cached_answer.get("reasoning", ""),
                        model_responses=cached_answer.get("model_responses", [])
                    )
                    consensus_results.append(cached_answer.get("consensus", False))
                else:
                    mcq_question = MCQQuestion(
                        question=question_text,
                        options=options,
                        correct_option=cached_answer.get("correct_option", 0),
                        confidence=cached_answer.get("confidence", 0),
                        reasoning=cached_answer.get("reasoning", "")
                    )
                    consensus_results.append(True)  # Single model always has "consensus"
                
                processed_questions.append(mcq_question)
                continue
            
            # Process with AI
            print(f"Processing question with AI: {question_text[:50]}...")
            
            if request.useMultiModel:
                answer_result = await ai_service.answer_mcq_multi_model(question_text, options)
                
                mcq_question = MCQQuestion(
                    question=question_text,
                    options=options,
                    correct_option=answer_result.get("correct_option", 0),
                    confidence=answer_result.get("confidence", 0),
                    reasoning=answer_result.get("reasoning", ""),
                    model_responses=answer_result.get("model_responses", [])
                )
                
                consensus_results.append(answer_result.get("consensus", False))
                
            else:
                answer_result = await ai_service.answer_mcq_single_model(question_text, options)
                
                mcq_question = MCQQuestion(
                    question=question_text,
                    options=options,
                    correct_option=answer_result.get("correct_option", 0),
                    confidence=answer_result.get("confidence", 0),
                    reasoning=answer_result.get("reasoning", "")
                )
                
                consensus_results.append(True)  # Single model always has "consensus"
            
            processed_questions.append(mcq_question)
            
            # Cache the answer
            await redis_service.cache_mcq_answer(question_text, options, answer_result)
        
        # Prepare final response
        response_data = {
            "questions": processed_questions,
            "processing_mode": processing_mode,
            "consensus": consensus_results,
            "total_questions": len(processed_questions),
            "cached": False
        }
        
        # Cache the full page analysis
        await redis_service.cache_full_page_analysis(
            request.url,
            request.content,
            response_data
        )
        
        return MCQDetectionResponse(**response_data)
        
    except Exception as e:
        print(f"Error in detect_mcqs: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing MCQs: {str(e)}")

@router.post("/answer-question", response_model=AnswerResponse)
async def answer_single_question(
    request: AnswerRequest,
    ai_service: AIService = Depends(get_ai_service),
    redis_service: RedisService = Depends(get_redis_service)
):
    """
    Answer a single MCQ question
    
    This endpoint processes a single question through AI model(s)
    """
    try:
        # Check cache first
        cached_answer = await redis_service.get_cached_mcq_answer(
            request.question, 
            request.options
        )
        
        if cached_answer:
            return AnswerResponse(**cached_answer)
        
        # Process with AI
        if request.useMultiModel:
            result = await ai_service.answer_mcq_multi_model(
                request.question, 
                request.options
            )
        else:
            result = await ai_service.answer_mcq_single_model(
                request.question, 
                request.options
            )
        
        # Cache the result
        await redis_service.cache_mcq_answer(
            request.question, 
            request.options, 
            result
        )
        
        return AnswerResponse(**result)
        
    except Exception as e:
        print(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")

@router.get("/health")
async def health_check(redis_service: RedisService = Depends(get_redis_service)):
    """Health check endpoint"""
    try:
        redis_status = await redis_service.ping()
        return {
            "status": "healthy",
            "redis": "connected" if redis_status else "disconnected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@router.get("/models")
async def get_available_models():
    """Get list of available AI models"""
    try:
        ai_service = AIService()
        return {
            "models": list(ai_service.models.keys()),
            "default_single": "gpt-4.1",
            "multi_model_set": ["gpt-4.1", "gemini-2.5-pro"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting models: {str(e)}")