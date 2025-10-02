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

router = APIRouter()

async def get_ai_service():
    """Dependency to get AI service instance"""
    return AIService()

@router.post("/detect-mcqs", response_model=MCQDetectionResponse)
async def detect_mcqs(
    request: PageContentRequest,
    ai_service: AIService = Depends(get_ai_service)
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
        
        # Extract MCQs from content
        print(f"Extracting MCQs from content (length: {len(request.content)})")
        
        extracted_mcqs = await ai_service.extract_mcqs_from_content(
            request.content, 
            request.layout
        )
        print(f"Extracted {len(extracted_mcqs)} MCQs from content")
        
        if not extracted_mcqs:
            return MCQDetectionResponse(
                questions=[],
                processing_mode=processing_mode,
                consensus=[],
                total_questions=0,
                cached=False
            )
        
        # Check if we should use batch processing (more efficient for multiple questions)
        if len(extracted_mcqs) > 1:
            print(f"Using batch processing for {len(extracted_mcqs)} questions...")
            
            # Prepare batch data
            questions_batch = []
            for mcq in extracted_mcqs:
                question_text = mcq.get("question", "")
                options = mcq.get("options", [])
                
                if question_text and options:
                    questions_batch.append({
                        "question": question_text,
                        "options": options
                    })
            
            # Process batch
            if questions_batch:
                batch_results = await ai_service.answer_multiple_mcqs_batch(
                    questions_batch, 
                    use_multi_model=request.useMultiModel
                )
                
                # Convert batch results to MCQQuestion objects
                processed_questions = []
                consensus_results = []
                
                for i, (mcq, result) in enumerate(zip(extracted_mcqs, batch_results)):
                    question_text = mcq.get("question", "")
                    options = mcq.get("options", [])
                    
                    if not question_text or not options:
                        continue
                    
                    if request.useMultiModel:
                        mcq_question = MCQQuestion(
                            question=question_text,
                            options=options,
                            correct_option=result.get("correct_option", 0),
                            confidence=result.get("confidence", 0),
                            reasoning=result.get("reasoning", ""),
                            model_responses=result.get("model_responses", [])
                        )
                        consensus_results.append(result.get("consensus", False))
                    else:
                        mcq_question = MCQQuestion(
                            question=question_text,
                            options=options,
                            correct_option=result.get("correct_option", 0),
                            confidence=result.get("confidence", 0),
                            reasoning=result.get("reasoning", "")
                        )
                        consensus_results.append(True)
                    
                    processed_questions.append(mcq_question)
        
        else:
            # Single question - use individual processing
            async def process_single_mcq(mcq):
                """Process a single MCQ and return the result"""
                try:
                    question_text = mcq.get("question", "")
                    options = mcq.get("options", [])
                    
                    if not question_text or not options:
                        return None
                    
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
                        
                        consensus = answer_result.get("consensus", False)
                        
                    else:
                        answer_result = await ai_service.answer_mcq_single_model(question_text, options)
                        
                        mcq_question = MCQQuestion(
                            question=question_text,
                            options=options,
                            correct_option=answer_result.get("correct_option", 0),
                            confidence=answer_result.get("confidence", 0),
                            reasoning=answer_result.get("reasoning", "")
                        )
                        
                        consensus = True  # Single model always has "consensus"
                    
                    return (mcq_question, consensus)
                
                except Exception as e:
                    print(f"Error in process_single_mcq: {e}")
                    return None
            
            # Process all MCQs concurrently
            print(f"Processing {len(extracted_mcqs)} MCQs in parallel...")
            mcq_tasks = [process_single_mcq(mcq) for mcq in extracted_mcqs]
            mcq_results = await asyncio.gather(*mcq_tasks, return_exceptions=True)
            
            # Filter out None results and exceptions
            processed_questions = []
            consensus_results = []
            
            for result in mcq_results:
                if isinstance(result, Exception):
                    print(f"Error processing MCQ: {result}")
                    continue
                
                if result is None:
                    continue
                
                if isinstance(result, tuple) and len(result) == 2:
                    mcq_question, consensus = result
                    processed_questions.append(mcq_question)
                    consensus_results.append(consensus)
                else:
                    print(f"Unexpected result format: {type(result)} - {result}")
                    continue
        
        # Prepare final response
        response_data = {
            "questions": processed_questions,
            "processing_mode": processing_mode,
            "consensus": consensus_results,
            "total_questions": len(processed_questions),
            "cached": False
        }
        
        return MCQDetectionResponse(**response_data)
        
    except Exception as e:
        print(f"Error in detect_mcqs: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing MCQs: {str(e)}")

@router.post("/answer-question", response_model=AnswerResponse)
async def answer_single_question(
    request: AnswerRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Answer a single MCQ question
    
    This endpoint processes a single question through AI model(s)
    """
    try:
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
        
        return AnswerResponse(**result)
        
    except Exception as e:
        print(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@router.get("/performance-stats")
async def get_performance_stats():
    """Get performance statistics for the AI service"""
    try:
        ai_service = AIService()
        
        # Basic configuration info
        stats = {
            "max_concurrent_requests": ai_service.max_concurrent_requests,
            "request_timeout": ai_service.request_timeout,
            "available_models": list(ai_service.models.keys()),
            "multi_model_enabled": len(ai_service.models) > 1,
            "batch_processing_enabled": True,
            "retry_configuration": {
                model_key: {
                    "max_retries": config.get("max_retries", 3),
                    "retry_delay": config.get("retry_delay", 1.0)
                }
                for model_key, config in ai_service.models.items()
            }
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance stats: {str(e)}")

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