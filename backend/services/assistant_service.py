"""
Personal Assistant Service for Atlas AI
Coordinates intent recognition and handler execution
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

from .intent_recognition import intent_recognizer, IntentType
from .handlers import BaseHandler, HandlerResponse
from .handlers.weather_handler import weather_handler
from .handlers.reminder_handler import reminder_handler
from .handlers.search_handler import search_handler

logger = logging.getLogger(__name__)

@dataclass
class AssistantRequest:
    """Request to the assistant service"""
    text: str
    user_id: str
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class AssistantResponse:
    """Response from the assistant service"""
    success: bool
    message: str
    intent_type: str
    confidence: float
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    requires_followup: bool = False
    followup_question: Optional[str] = None
    is_assistant_task: bool = False

class AssistantService:
    """Main service for personal assistant capabilities"""
    
    def __init__(self):
        self.handlers: Dict[IntentType, BaseHandler] = {
            IntentType.WEATHER: weather_handler,
            IntentType.REMINDER: reminder_handler,
            IntentType.SEARCH: search_handler,
        }
        self.confidence_threshold = 0.6
        
    async def process_request(self, request: AssistantRequest) -> AssistantResponse:
        """Process an assistant request"""
        try:
            # Recognize intent
            intent = intent_recognizer.recognize_intent(request.text)
            
            logger.info(f"Recognized intent: {intent.type.value} with confidence {intent.confidence}")
            
            # Check if this is an assistant task
            is_assistant_task = (
                intent.type != IntentType.UNKNOWN and 
                intent.type != IntentType.GENERAL_CHAT and
                intent.confidence >= self.confidence_threshold
            )
            
            if not is_assistant_task:
                return AssistantResponse(
                    success=True,
                    message="This doesn't appear to be a personal assistant task. I'll handle it as a general conversation.",
                    intent_type=intent.type.value,
                    confidence=intent.confidence,
                    is_assistant_task=False
                )
            
            # Get the appropriate handler
            handler = self.handlers.get(intent.type)
            if not handler:
                return AssistantResponse(
                    success=False,
                    message=f"I understand you want help with {intent.type.value}, but that feature isn't available yet.",
                    intent_type=intent.type.value,
                    confidence=intent.confidence,
                    error=f"No handler available for {intent.type.value}",
                    is_assistant_task=True
                )
            
            # Validate required entities
            required_entities = intent_recognizer.get_required_entities(intent.type, intent.action)
            missing_entities = self._check_missing_entities(intent.entities, required_entities)
            
            if missing_entities:
                followup_question = self._generate_followup_question(intent.type, intent.action, missing_entities)
                return AssistantResponse(
                    success=True,
                    message="I need a bit more information to help you with that.",
                    intent_type=intent.type.value,
                    confidence=intent.confidence,
                    requires_followup=True,
                    followup_question=followup_question,
                    is_assistant_task=True
                )
            
            # Execute the handler
            handler_response = await handler.execute(intent, intent.entities, request.context)
            
            return AssistantResponse(
                success=handler_response.success,
                message=handler_response.message,
                intent_type=intent.type.value,
                confidence=intent.confidence,
                data=handler_response.data,
                error=handler_response.error,
                requires_followup=handler_response.requires_followup,
                followup_question=handler_response.followup_question,
                is_assistant_task=True
            )
            
        except Exception as e:
            logger.error(f"Error processing assistant request: {str(e)}")
            return AssistantResponse(
                success=False,
                message="I encountered an error while processing your request. Please try again.",
                intent_type="error",
                confidence=0.0,
                error=str(e),
                is_assistant_task=True
            )
    
    def _check_missing_entities(self, entities: List, required_entities: List[str]) -> List[str]:
        """Check which required entities are missing"""
        entity_types = [entity.type for entity in entities]
        return [req for req in required_entities if req not in entity_types]
    
    def _generate_followup_question(self, intent_type: IntentType, action: str, missing_entities: List[str]) -> str:
        """Generate a followup question for missing entities"""
        questions = {
            IntentType.WEATHER: {
                "location": "Which city or location would you like the weather for?",
                "datetime": "For what date would you like the weather forecast?"
            },
            IntentType.REMINDER: {
                "topic": "What would you like me to remind you about?",
                "datetime": "When would you like to be reminded? (e.g., 'tomorrow at 3pm', 'in 2 hours')"
            },
            IntentType.SEARCH: {
                "topic": "What would you like me to search for?"
            },
            IntentType.CALENDAR: {
                "datetime": "When would you like to schedule this? (e.g., 'tomorrow at 2pm', 'next Monday')",
                "topic": "What is this meeting or event about?"
            },
            IntentType.EMAIL: {
                "person": "Who would you like to send this email to?",
                "topic": "What is the subject or content of the email?"
            }
        }
        
        intent_questions = questions.get(intent_type, {})
        
        if len(missing_entities) == 1:
            entity = missing_entities[0]
            return intent_questions.get(entity, f"I need more information about the {entity}.")
        else:
            # Multiple missing entities
            entity_questions = [intent_questions.get(entity, entity) for entity in missing_entities]
            return f"I need to know: {', '.join(entity_questions)}"
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get available assistant capabilities"""
        capabilities = {
            "weather": {
                "description": "Get current weather and forecasts",
                "actions": ["current", "forecast", "conditions"],
                "examples": [
                    "What's the weather like?",
                    "Will it rain tomorrow?",
                    "Weather forecast for New York"
                ]
            },
            "reminders": {
                "description": "Create and manage reminders",
                "actions": ["create", "list", "update", "delete"],
                "examples": [
                    "Remind me to call mom at 3pm",
                    "Set a reminder for my meeting tomorrow",
                    "What are my reminders?"
                ]
            },
            "search": {
                "description": "Search the web for information",
                "actions": ["web_search", "information", "lookup"],
                "examples": [
                    "Search for the latest news about AI",
                    "What is the capital of France?",
                    "Find information about climate change"
                ]
            }
        }
        
        return {
            "available_capabilities": capabilities,
            "confidence_threshold": self.confidence_threshold,
            "supported_intents": [intent.value for intent in IntentType if intent != IntentType.UNKNOWN]
        }

# Global instance
assistant_service = AssistantService()
