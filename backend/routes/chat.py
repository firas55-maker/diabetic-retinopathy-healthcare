"""
Chat route for Gemini-powered educational assistant
Handles POST requests for diabetes/DR educational conversations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from typing import Optional
from pathlib import Path

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Gemini API configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# Model fallback list - try primary first, then fallbacks if 404
AVAILABLE_MODELS = [
    "gemini-3.6-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

# Load diabetes knowledge base
def load_knowledge_base() -> str:
    """Load the diabetes education knowledge base from extracted PDF"""
    knowledge_file = Path(__file__).parent.parent / "knowledge" / "diabetes_education.txt"
    try:
        if knowledge_file.exists():
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception:
        pass
    return ""

# Load knowledge base on startup
KNOWLEDGE_BASE = load_knowledge_base()

# System prompt for the educational assistant with knowledge base
SYSTEM_PROMPT = f"""You are a helpful assistant providing general educational information about diabetes and diabetic retinopathy.
You do not diagnose, do not interpret the user's specific scan results, and do not replace medical advice -- always encourage the user to discuss any concerns with their doctor.

Key guidelines:
- Provide accurate, evidence-based information about diabetes management and diabetic retinopathy
- Explain what DR is, risk factors, and prevention strategies
- Do not provide personalized medical advice or diagnosis
- If asked about personal symptoms or results, redirect to their healthcare provider
- Keep responses clear, compassionate, and accessible to patients
- Use simple language, avoid excessive medical jargon

Use the following educational context to answer questions accurately:

{KNOWLEDGE_BASE if KNOWLEDGE_BASE else "Note: Knowledge base not loaded. Provide general information based on your training."}

Always encourage users to discuss any health concerns with their doctor."""

class ChatMessage(BaseModel):
    """Chat message request model"""
    message: str
    conversation_history: Optional[list] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str

@router.post("/send", response_model=ChatResponse)
async def send_chat_message(request: ChatMessage):
    """
    Send a message to Gemini and get an educational response
    Automatically tries fallback models if primary model returns 404

    Args:
        request: ChatMessage containing the user's message and optional conversation history

    Returns:
        ChatResponse with the assistant's reply
    """

    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key not configured. Set GEMINI_API_KEY environment variable."
        )

    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Build conversation for Gemini
    messages = []

    # Add conversation history if provided
    if request.conversation_history:
        for msg in request.conversation_history:
            messages.append({
                "role": msg.get("role", "user"),
                "parts": [{"text": msg.get("content", "")}]
            })

    # Add current message
    messages.append({
        "role": "user",
        "parts": [{"text": request.message}]
    })

    # Try each model in the fallback list
    last_error = None

    try:
        async with httpx.AsyncClient() as client:
            for model in AVAILABLE_MODELS:
                try:
                    # Construct correct URL: base/model:method
                    url = f"{GEMINI_API_BASE}/{model}:generateContent"

                    response = await client.post(
                        url,
                        params={"key": GEMINI_API_KEY},
                        json={
                            "system_instruction": {
                                "parts": [{"text": SYSTEM_PROMPT}]
                            },
                            "contents": messages,
                            "generationConfig": {
                                "temperature": 0.7,
                                "topK": 40,
                                "topP": 0.95,
                                "maxOutputTokens": 500,
                            }
                        },
                        timeout=30.0
                    )

                    # If successful, process response
                    if response.status_code == 200:
                        result = response.json()

                        # Extract response text
                        if "candidates" in result and len(result["candidates"]) > 0:
                            candidate = result["candidates"][0]
                            if "content" in candidate and "parts" in candidate["content"]:
                                parts = candidate["content"]["parts"]
                                if len(parts) > 0:
                                    assistant_message = parts[0].get("text", "")
                                    if assistant_message:
                                        return ChatResponse(response=assistant_message)

                        raise HTTPException(
                            status_code=500,
                            detail="Unexpected response format from Gemini API"
                        )

                    # If 404, try next model
                    elif response.status_code == 404:
                        last_error = f"Model {model} not found"
                        continue

                    # Other errors - fail immediately
                    else:
                        error_detail = response.text[:200]  # Limit error detail length
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"Gemini API error: {error_detail}"
                        )

                except httpx.TimeoutException:
                    last_error = f"Model {model} timed out"
                    continue
                except httpx.RequestError as e:
                    last_error = f"Model {model} connection failed"
                    continue
                except HTTPException:
                    raise

        # If all models failed
        if last_error:
            raise HTTPException(
                status_code=503,
                detail=f"All models unavailable. Last: {last_error}"
            )
        else:
            raise HTTPException(
                status_code=503,
                detail="Failed to get response from Gemini API"
            )

    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Gemini API request timed out. Please try again."
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail="Failed to connect to Gemini API"
        )
    except Exception as e:
        # Avoid Unicode encoding issues
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request"
        )
