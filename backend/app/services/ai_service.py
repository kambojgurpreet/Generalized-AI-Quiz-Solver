import openai
import google.generativeai as genai
import asyncio
import json
import os
from typing import List, Dict, Optional, Tuple, Any
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        # OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        openai.api_key = self.openai_api_key
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Google Gemini configuration
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
        
        # Available models from different providers
        self.models = {
            "gpt-4.1": {
                "name": "GPT-4.1",
                "provider": "openai",
                "model_id": "gpt-4.1",
                "temperature": 0.3
            },
            "gemini-2.5-pro": {
                "name": "Gemini 2.5 Pro",
                "provider": "google",
                "model_id": "gemini-2.5-pro",
                "temperature": 0.3
            }
        }

    async def extract_mcqs_from_content(self, content: str, layout_info: Dict) -> List[Dict]:
        """Extract MCQ questions from webpage content using AI"""
        
        system_prompt = """You are an expert at identifying and extracting multiple choice questions (MCQs) from webpage content.

Your task is to:
1. Identify all multiple choice questions in the provided content
2. Extract the question text and all available options
3. Return structured data for each question found

Guidelines:
- Look for questions followed by multiple choice options (A, B, C, D, etc.)
- Options may be formatted as: A) option, (A) option, A. option, or similar
- Questions may be numbered or unnumbered
- Include all context necessary to understand the question
- If no MCQs are found, return an empty list

Return a JSON array where each object has:
{
    "question": "The complete question text",
    "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
    "question_index": 0
}"""

        user_prompt = f"""Analyze this webpage content and extract all MCQ questions:

Content:
{content[:8000]}  # Limit content to avoid token limits

Layout Info:
URL: {layout_info.get('url', 'Unknown')}
Title: {layout_info.get('title', 'Unknown')}

Extract all multiple choice questions with their options."""

        try:
            response = await self._make_openai_request(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            
            if response and response.choices:
                content_text = response.choices[0].message.content
                
                if content_text:
                    # Try to parse JSON from the response
                    try:
                        # Look for JSON in the response
                        start_idx = content_text.find('[')
                        end_idx = content_text.rfind(']') + 1
                        
                        if start_idx != -1 and end_idx != 0:
                            json_str = content_text[start_idx:end_idx]
                            mcqs = json.loads(json_str)
                            
                            # Validate the structure
                            validated_mcqs = []
                            for i, mcq in enumerate(mcqs):
                                if isinstance(mcq, dict) and 'question' in mcq and 'options' in mcq:
                                    mcq['question_index'] = i
                                    validated_mcqs.append(mcq)
                            
                            return validated_mcqs
                        else:
                            print("No JSON structure found in AI response")
                            return []
                            
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse JSON from AI response: {e}")
                        print(f"Response content: {content_text}")
                        return []
                else:
                    print("Empty response from AI")
                    return []
                
        except Exception as e:
            print(f"Error extracting MCQs: {e}")
            return []

    async def answer_mcq_single_model(self, question: str, options: List[str]) -> Dict:
        """Answer an MCQ using a single AI model (GPT-4.1)"""
        
        system_prompt = """You are an expert at answering multiple choice questions. Analyze the question and options carefully, then provide:

1. The correct answer (as option index: 0, 1, 2, or 3)
2. Your confidence level (0-100%)
3. Detailed reasoning for your choice

Return your response in this exact JSON format:
{
    "correct_option": 0,
    "confidence": 85,
    "reasoning": "Detailed explanation of why this option is correct"
}"""

        options_text = "\n".join([f"{chr(65 + i)}. {option}" for i, option in enumerate(options)])
        
        user_prompt = f"""Question: {question}

Options:
{options_text}

Analyze this question and provide the correct answer with reasoning."""

        try:
            response = await self._make_openai_request(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            if response and response.choices:
                content_text = response.choices[0].message.content
                
                if content_text:
                    # Parse JSON response
                    try:
                        start_idx = content_text.find('{')
                        end_idx = content_text.rfind('}') + 1
                        
                        if start_idx != -1 and end_idx != 0:
                            json_str = content_text[start_idx:end_idx]
                            result = json.loads(json_str)
                            
                            # Validate required fields
                            if all(key in result for key in ['correct_option', 'confidence', 'reasoning']):
                                # Ensure correct_option is within valid range
                                if 0 <= result['correct_option'] < len(options):
                                    return result
                        
                        # If parsing fails, return default response
                        return {
                            "correct_option": 0,
                            "confidence": 50,
                            "reasoning": "Could not parse AI response properly"
                        }
                        
                    except json.JSONDecodeError:
                        return {
                            "correct_option": 0,
                            "confidence": 50,
                            "reasoning": "Failed to parse AI response as JSON"
                        }
                else:
                    return {
                        "correct_option": 0,
                        "confidence": 50,
                        "reasoning": "Empty response from AI"
                    }
                
        except Exception as e:
            print(f"Error answering MCQ: {e}")
            return {
                "correct_option": 0,
                "confidence": 0,
                "reasoning": f"Error occurred: {str(e)}"
            }

    async def answer_mcq_multi_model(self, question: str, options: List[str]) -> Dict:
        """Answer an MCQ using multiple AI services (OpenAI GPT-4 + Google Gemini) and check for consensus"""
        
        # Use different AI providers
        models_to_use = ["gpt-4.1", "gemini-2.5-pro"]
        
        # Get responses from all models
        tasks = []
        for model_key in models_to_use:
            if model_key in self.models:
                task = self._answer_with_specific_model(question, options, model_key)
                tasks.append(task)
        
        # Wait for all responses
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process responses
        model_responses = []
        option_votes = {}
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Error from model {models_to_use[i]}: {response}")
                continue
                
            if response and isinstance(response, dict):
                model_name = self.models[models_to_use[i]]["name"]
                model_response = {
                    "model": model_name,
                    "selected_option": response.get("correct_option", 0),
                    "confidence": response.get("confidence", 0),
                    "reasoning": response.get("reasoning", "No reasoning provided")
                }
                model_responses.append(model_response)
                
                # Count votes
                option_idx = response.get("correct_option", 0)
                option_votes[option_idx] = option_votes.get(option_idx, 0) + 1
        
        # Determine consensus
        consensus_achieved = False
        final_answer = 0
        final_confidence = 0
        
        if option_votes:
            # Find the most voted option
            final_answer = max(option_votes.keys(), key=lambda x: option_votes[x])
            max_votes = option_votes[final_answer]
            total_models = len(model_responses)
            
            # Consensus if more than half agree
            consensus_achieved = max_votes > total_models / 2
            
            # Calculate weighted confidence
            total_confidence = sum(
                resp["confidence"] for resp in model_responses 
                if resp["selected_option"] == final_answer
            )
            contributing_models = sum(
                1 for resp in model_responses 
                if resp["selected_option"] == final_answer
            )
            
            if contributing_models > 0:
                final_confidence = total_confidence / contributing_models
            else:
                final_confidence = 50
        
        # Create comprehensive reasoning
        reasoning_parts = []
        if consensus_achieved:
            reasoning_parts.append(f"CONSENSUS ACHIEVED: {option_votes[final_answer]} out of {len(model_responses)} AI services agree on option {chr(65 + final_answer)}.")
        else:
            reasoning_parts.append("NO CONSENSUS: AI services disagree on the correct answer.")
            reasoning_parts.append(f"Vote distribution: {option_votes}")
        
        reasoning_parts.append("\nIndividual AI service responses:")
        for resp in model_responses:
            reasoning_parts.append(f"- {resp['model']}: Option {chr(65 + resp['selected_option'])} ({resp['confidence']}% confidence)")
        
        final_reasoning = "\n".join(reasoning_parts)
        
        return {
            "correct_option": final_answer,
            "confidence": final_confidence,
            "reasoning": final_reasoning,
            "model_responses": model_responses,
            "consensus": consensus_achieved
        }

    async def _answer_with_specific_model(self, question: str, options: List[str], model_key: str) -> Dict:
        """Answer MCQ with a specific AI service (OpenAI or Google)"""
        
        model_config = self.models[model_key]
        provider = model_config["provider"]
        
        if provider == "openai":
            return await self._answer_with_openai(question, options, model_config)
        elif provider == "google":
            return await self._answer_with_gemini(question, options, model_config)
        else:
            return {
                "correct_option": 0,
                "confidence": 0,
                "reasoning": f"Unknown provider: {provider}"
            }

    async def _answer_with_openai(self, question: str, options: List[str], model_config: Dict) -> Dict:
        """Answer MCQ using OpenAI GPT model"""
        
        system_prompt = f"""You are {model_config['name']}, an expert at answering multiple choice questions. Analyze the question and options carefully, then provide:

1. The correct answer (as option index: 0, 1, 2, or 3)
2. Your confidence level (0-100%)
3. Detailed reasoning for your choice

Return your response in this exact JSON format:
{{
    "correct_option": 0,
    "confidence": 85,
    "reasoning": "Detailed explanation of why this option is correct"
}}"""

        options_text = "\n".join([f"{chr(65 + i)}. {option}" for i, option in enumerate(options)])
        
        user_prompt = f"""Question: {question}

Options:
{options_text}

Analyze this question and provide the correct answer with reasoning."""

        try:
            response = await self._make_openai_request(
                model=model_config["model_id"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=model_config["temperature"]
            )
            
            if response and response.choices:
                content_text = response.choices[0].message.content
                
                if content_text:
                    # Parse JSON response
                    try:
                        start_idx = content_text.find('{')
                        end_idx = content_text.rfind('}') + 1
                        
                        if start_idx != -1 and end_idx != 0:
                            json_str = content_text[start_idx:end_idx]
                            result = json.loads(json_str)
                            
                            if all(key in result for key in ['correct_option', 'confidence', 'reasoning']):
                                if 0 <= result['correct_option'] < len(options):
                                    return result
                        
                        return {
                            "correct_option": 0,
                            "confidence": 50,
                            "reasoning": f"Could not parse {model_config['name']} response properly"
                        }
                        
                    except json.JSONDecodeError:
                        return {
                            "correct_option": 0,
                            "confidence": 50,
                            "reasoning": f"Failed to parse {model_config['name']} response as JSON"
                        }
                else:
                    return {
                        "correct_option": 0,
                        "confidence": 50,
                        "reasoning": f"Empty response from {model_config['name']}"
                    }
                
        except Exception as e:
            return {
                "correct_option": 0,
                "confidence": 0,
                "reasoning": f"Error from {model_config['name']}: {str(e)}"
            }

    async def _answer_with_gemini(self, question: str, options: List[str], model_config: Dict) -> Dict:
        """Answer MCQ using Google Gemini model"""
        
        if not self.google_api_key:
            return {
                "correct_option": 0,
                "confidence": 0,
                "reasoning": "Google API key not configured"
            }
        
        prompt = f"""You are {model_config['name']}, an expert at answering multiple choice questions. Analyze the question and options carefully, then provide:

1. The correct answer (as option index: 0, 1, 2, or 3)
2. Your confidence level (0-100%)
3. Detailed reasoning for your choice

Question: {question}

Options:
{chr(10).join([f"{chr(65 + i)}. {option}" for i, option in enumerate(options)])}

Return your response in this exact JSON format:
{{
    "correct_option": 0,
    "confidence": 85,
    "reasoning": "Detailed explanation of why this option is correct"
}}

Analyze this question and provide the correct answer with reasoning."""

        try:
            # Create the model
            model = genai.GenerativeModel(model_config["model_id"])
            
            # Generate response
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=model_config["temperature"],
                    max_output_tokens=1000,
                )
            )
            
            if response and response.text:
                content_text = response.text
                
                # Parse JSON response
                try:
                    start_idx = content_text.find('{')
                    end_idx = content_text.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx != 0:
                        json_str = content_text[start_idx:end_idx]
                        result = json.loads(json_str)
                        
                        if all(key in result for key in ['correct_option', 'confidence', 'reasoning']):
                            if 0 <= result['correct_option'] < len(options):
                                return result
                    
                    return {
                        "correct_option": 0,
                        "confidence": 50,
                        "reasoning": f"Could not parse {model_config['name']} response properly"
                    }
                    
                except json.JSONDecodeError:
                    return {
                        "correct_option": 0,
                        "confidence": 50,
                        "reasoning": f"Failed to parse {model_config['name']} response as JSON"
                    }
            else:
                return {
                    "correct_option": 0,
                    "confidence": 50,
                    "reasoning": f"Empty response from {model_config['name']}"
                }
                
        except Exception as e:
            return {
                "correct_option": 0,
                "confidence": 0,
                "reasoning": f"Error from {model_config['name']}: {str(e)}"
            }

    async def _make_openai_request(self, model: str, messages: List[Dict[str, Any]], temperature: float = 0.3):
        """Make an OpenAI API request with error handling"""
        try:
            # Convert messages to proper format for OpenAI
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=model,
                messages=formatted_messages,  # type: ignore
                temperature=temperature,
                max_tokens=2000
            )
            return response
        except Exception as e:
            print(f"OpenAI API request failed: {e}")
            raise