"""
Assistant API endpoints for Atlas AI
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from .assistant_service import assistant_service, AssistantRequest
from .supabase import get_user_id

logger = logging.getLogger(__name__)

router = APIRouter()

class AssistantQueryRequest(BaseModel):
    text: str
    context: Optional[Dict[str, Any]] = None

class AssistantQueryResponse(BaseModel):
    success: bool
    message: str
    intent_type: str
    confidence: float
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    requires_followup: bool = False
    followup_question: Optional[str] = None
    is_assistant_task: bool = False

@router.post("/assistant/query", response_model=AssistantQueryResponse)
async def query_assistant(
    request: AssistantQueryRequest,
    user_id: str = Depends(get_user_id)
):
    """
    Process a query through the personal assistant
    """
    try:
        assistant_request = AssistantRequest(
            text=request.text,
            user_id=user_id,
            context=request.context or {}
        )
        
        response = await assistant_service.process_request(assistant_request)
        
        return AssistantQueryResponse(
            success=response.success,
            message=response.message,
            intent_type=response.intent_type,
            confidence=response.confidence,
            data=response.data,
            error=response.error,
            requires_followup=response.requires_followup,
            followup_question=response.followup_question,
            is_assistant_task=response.is_assistant_task
        )
        
    except Exception as e:
        logger.error(f"Error in assistant query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assistant/capabilities")
async def get_assistant_capabilities():
    """
    Get available assistant capabilities and features
    """
    try:
        capabilities = await assistant_service.get_capabilities()
        return capabilities
        
    except Exception as e:
        logger.error(f"Error getting assistant capabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class IntentTestRequest(BaseModel):
    text: str

@router.post("/assistant/test-intent")
async def test_intent_recognition(request: IntentTestRequest):
    """
    Test intent recognition without executing handlers (for debugging)
    """
    try:
        from .intent_recognition import intent_recognizer
        
        intent = intent_recognizer.recognize_intent(request.text)
        
        return {
            "text": request.text,
            "intent_type": intent.type.value,
            "confidence": intent.confidence,
            "action": intent.action,
            "entities": [
                {
                    "type": entity.type,
                    "value": entity.value,
                    "confidence": entity.confidence,
                    "start_pos": entity.start_pos,
                    "end_pos": entity.end_pos
                }
                for entity in intent.entities
            ],
            "required_entities": intent_recognizer.get_required_entities(intent.type, intent.action or "")
        }
        
    except Exception as e:
        logger.error(f"Error testing intent recognition: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Weather-specific endpoints
@router.get("/assistant/weather/current")
async def get_current_weather(
    location: Optional[str] = None,
    user_id: str = Depends(get_user_id)
):
    """
    Get current weather for a location
    """
    try:
        from .handlers.weather_handler import weather_handler
        from .intent_recognition import IntentType
        
        # Create a mock intent for weather
        class MockIntent:
            type = IntentType.WEATHER
            action = "current"
            entities = []
        
        entities = []
        if location:
            from .intent_recognition import Entity
            entities.append(Entity(type="location", value=location, confidence=1.0))
        
        response = await weather_handler.execute(MockIntent(), entities, {})
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current weather: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Reminder-specific endpoints
@router.get("/assistant/reminders")
async def get_reminders(user_id: str = Depends(get_user_id)):
    """
    Get all active reminders for the user
    """
    try:
        from .handlers.reminder_handler import reminder_handler
        from .intent_recognition import IntentType
        
        # Create a mock intent for listing reminders
        class MockIntent:
            type = IntentType.REMINDER
            action = "list"
        
        response = await reminder_handler.execute(MockIntent(), [], {"user_id": user_id})
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reminders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class CreateReminderRequest(BaseModel):
    title: str
    due_date: str  # ISO format or natural language
    description: Optional[str] = None

@router.post("/assistant/reminders")
async def create_reminder(
    request: CreateReminderRequest,
    user_id: str = Depends(get_user_id)
):
    """
    Create a new reminder
    """
    try:
        from .handlers.reminder_handler import reminder_handler
        from .intent_recognition import IntentType, Entity
        
        # Create entities for the reminder
        entities = [
            Entity(type="topic", value=request.title, confidence=1.0),
            Entity(type="datetime", value=request.due_date, confidence=1.0)
        ]
        
        # Create a mock intent for creating reminder
        class MockIntent:
            type = IntentType.REMINDER
            action = "create"
        
        response = await reminder_handler.execute(MockIntent(), entities, {"user_id": user_id})
        
        if response.success:
            return response.data
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating reminder: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/assistant/reminders/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    user_id: str = Depends(get_user_id)
):
    """
    Delete a reminder by ID
    """
    try:
        from .handlers.reminder_handler import reminder_handler
        from .intent_recognition import IntentType, Entity
        
        # Create entity for the reminder ID
        entities = [Entity(type="topic", value=reminder_id, confidence=1.0)]
        
        # Create a mock intent for deleting reminder
        class MockIntent:
            type = IntentType.REMINDER
            action = "delete"
        
        response = await reminder_handler.execute(MockIntent(), entities, {"user_id": user_id})
        
        if response.success:
            return {"message": "Reminder deleted successfully"}
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting reminder: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
