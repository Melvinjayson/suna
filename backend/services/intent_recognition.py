"""
Intent Recognition Service for Atlas AI
Classifies user intents for personal assistant capabilities
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Supported intent types for Atlas AI"""
    CALENDAR = "calendar"
    EMAIL = "email"
    REMINDER = "reminder"
    WEATHER = "weather"
    NEWS = "news"
    SEARCH = "search"
    GENERAL_CHAT = "general_chat"
    UNKNOWN = "unknown"

@dataclass
class Entity:
    """Extracted entity from user input"""
    type: str
    value: str
    confidence: float
    start_pos: int = 0
    end_pos: int = 0

@dataclass
class Intent:
    """Recognized intent with entities and confidence"""
    type: IntentType
    confidence: float
    entities: List[Entity]
    raw_text: str
    action: Optional[str] = None
    
class IntentRecognizer:
    """Rule-based intent recognition with pattern matching"""
    
    def __init__(self):
        self.patterns = self._load_patterns()
        self.entity_extractors = self._load_entity_extractors()
    
    def _load_patterns(self) -> Dict[IntentType, List[Dict]]:
        """Load intent recognition patterns"""
        return {
            IntentType.CALENDAR: [
                {
                    "patterns": [
                        r"(?:schedule|create|add|set up|book)\s+(?:a\s+)?(?:meeting|appointment|event)",
                        r"(?:what|when)\s+(?:is|are)\s+(?:my|the)\s+(?:next|upcoming)\s+(?:meeting|appointment|event)",
                        r"(?:cancel|delete|remove)\s+(?:my|the)\s+(?:meeting|appointment|event)",
                        r"(?:reschedule|move|change)\s+(?:my|the)\s+(?:meeting|appointment|event)",
                        r"(?:check|show|list)\s+(?:my|the)\s+(?:calendar|schedule|appointments)",
                    ],
                    "actions": ["create", "read", "update", "delete", "list"]
                }
            ],
            IntentType.EMAIL: [
                {
                    "patterns": [
                        r"(?:send|compose|write)\s+(?:an?\s+)?email",
                        r"(?:check|read|show)\s+(?:my\s+)?(?:email|inbox|messages)",
                        r"(?:reply|respond)\s+to\s+(?:the\s+)?email",
                        r"(?:forward|share)\s+(?:this\s+|the\s+)?email",
                        r"(?:delete|remove)\s+(?:this\s+|the\s+)?email",
                    ],
                    "actions": ["send", "read", "reply", "forward", "delete"]
                }
            ],
            IntentType.REMINDER: [
                {
                    "patterns": [
                        r"(?:remind|alert)\s+me\s+(?:to|about)",
                        r"(?:set|create|add)\s+(?:a\s+)?(?:reminder|alert|notification)",
                        r"(?:don't\s+forget|remember)\s+to",
                        r"(?:what|show)\s+(?:are\s+)?(?:my\s+)?(?:reminders|alerts|tasks)",
                        r"(?:cancel|delete|remove)\s+(?:the\s+)?(?:reminder|alert)",
                    ],
                    "actions": ["create", "read", "update", "delete", "list"]
                }
            ],
            IntentType.WEATHER: [
                {
                    "patterns": [
                        r"(?:what|how)\s+(?:is|will)\s+(?:the\s+)?weather",
                        r"(?:weather\s+)?(?:forecast|report|conditions)",
                        r"(?:is\s+it|will\s+it)\s+(?:rain|snow|sunny|cloudy)",
                        r"(?:temperature|temp)\s+(?:today|tomorrow|outside)",
                        r"(?:should\s+i|do\s+i\s+need)\s+(?:bring\s+)?(?:an?\s+)?(?:umbrella|jacket|coat)",
                    ],
                    "actions": ["current", "forecast", "conditions"]
                }
            ],
            IntentType.NEWS: [
                {
                    "patterns": [
                        r"(?:what|show)\s+(?:is|are)\s+(?:the\s+)?(?:latest\s+)?news",
                        r"(?:news|headlines|updates)\s+(?:about|on|for)",
                        r"(?:what|anything)\s+(?:new|happening)\s+(?:in|about|with)",
                        r"(?:current\s+)?(?:events|affairs|happenings)",
                        r"(?:breaking|latest)\s+news",
                    ],
                    "actions": ["headlines", "search", "category"]
                }
            ],
            IntentType.SEARCH: [
                {
                    "patterns": [
                        r"(?:search|look up|find|google)\s+(?:for\s+)?",
                        r"(?:what|who|where|when|why|how)\s+(?:is|are|was|were|do|does|did)",
                        r"(?:tell|show)\s+me\s+(?:about|more\s+about)",
                        r"(?:information|info|details)\s+(?:about|on|for)",
                        r"(?:can\s+you\s+)?(?:help\s+me\s+)?(?:find|locate)",
                    ],
                    "actions": ["web_search", "information", "lookup"]
                }
            ]
        }
    
    def _load_entity_extractors(self) -> Dict[str, List[str]]:
        """Load entity extraction patterns"""
        return {
            "datetime": [
                r"(?:today|tomorrow|yesterday)",
                r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
                r"(?:january|february|march|april|may|june|july|august|september|october|november|december)",
                r"\d{1,2}:\d{2}(?:\s*(?:am|pm))?",
                r"\d{1,2}/\d{1,2}(?:/\d{2,4})?",
                r"(?:in\s+)?\d+\s+(?:minutes?|hours?|days?|weeks?|months?)",
                r"(?:next|this)\s+(?:week|month|year)",
                r"(?:at\s+)?\d{1,2}(?::\d{2})?\s*(?:am|pm)",
            ],
            "location": [
                r"(?:in|at|near|around)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*",
                r"[A-Z][a-z]+,\s*[A-Z]{2}",
                r"\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)",
            ],
            "person": [
                r"(?:with|to|from)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*",
                r"[A-Z][a-z]+@[a-z]+\.[a-z]+",
            ],
            "duration": [
                r"\d+\s+(?:minutes?|hours?|days?|weeks?|months?|years?)",
                r"(?:for\s+)?\d+\s*(?:min|hr|h|d|w|m|y)",
                r"(?:half\s+an?\s+|quarter\s+)?hour",
            ],
            "topic": [
                r"(?:about|regarding|concerning)\s+([^,.!?]+)",
                r"(?:subject|topic):\s*([^,.!?]+)",
            ]
        }
    
    def recognize_intent(self, text: str) -> Intent:
        """Recognize intent from user input text"""
        text_lower = text.lower().strip()
        
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        best_action = None
        
        # Check each intent type
        for intent_type, pattern_groups in self.patterns.items():
            for pattern_group in pattern_groups:
                for pattern in pattern_group["patterns"]:
                    match = re.search(pattern, text_lower)
                    if match:
                        confidence = self._calculate_confidence(match, text_lower, pattern)
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_intent = intent_type
                            best_action = self._extract_action(text_lower, pattern_group["actions"])
        
        # If no specific intent found, check if it's a general question
        if best_intent == IntentType.UNKNOWN:
            if self._is_general_chat(text_lower):
                best_intent = IntentType.GENERAL_CHAT
                best_confidence = 0.7
        
        # Extract entities
        entities = self._extract_entities(text)
        
        return Intent(
            type=best_intent,
            confidence=best_confidence,
            entities=entities,
            raw_text=text,
            action=best_action
        )
    
    def _calculate_confidence(self, match: re.Match, text: str, pattern: str) -> float:
        """Calculate confidence score for a pattern match"""
        base_confidence = 0.8
        
        # Boost confidence for exact matches
        if match.group(0) == text:
            base_confidence += 0.15
        
        # Boost confidence for longer matches
        match_length = len(match.group(0))
        text_length = len(text)
        length_ratio = match_length / text_length
        base_confidence += length_ratio * 0.1
        
        return min(base_confidence, 1.0)
    
    def _extract_action(self, text: str, possible_actions: List[str]) -> Optional[str]:
        """Extract the specific action from text"""
        for action in possible_actions:
            if action in text:
                return action
        
        # Default action mapping based on keywords
        if any(word in text for word in ["create", "add", "set", "schedule", "send", "compose"]):
            return "create"
        elif any(word in text for word in ["show", "list", "check", "read", "what", "when"]):
            return "read"
        elif any(word in text for word in ["update", "change", "modify", "edit", "reschedule"]):
            return "update"
        elif any(word in text for word in ["delete", "remove", "cancel"]):
            return "delete"
        
        return possible_actions[0] if possible_actions else None
    
    def _is_general_chat(self, text: str) -> bool:
        """Check if text is general conversation"""
        chat_indicators = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "what's up", "thanks", "thank you", "please", "sorry",
            "yes", "no", "okay", "ok", "sure", "maybe", "i think", "i believe"
        ]
        
        return any(indicator in text for indicator in chat_indicators)
    
    def _extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text"""
        entities = []
        
        for entity_type, patterns in self.entity_extractors.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = Entity(
                        type=entity_type,
                        value=match.group(0).strip(),
                        confidence=0.8,
                        start_pos=match.start(),
                        end_pos=match.end()
                    )
                    entities.append(entity)
        
        return entities
    
    def get_required_entities(self, intent_type: IntentType, action: str) -> List[str]:
        """Get required entities for a specific intent and action"""
        requirements = {
            IntentType.CALENDAR: {
                "create": ["datetime"],
                "read": [],
                "update": ["datetime"],
                "delete": ["datetime"],
                "list": []
            },
            IntentType.EMAIL: {
                "send": ["person", "topic"],
                "read": [],
                "reply": ["topic"],
                "forward": ["person"],
                "delete": []
            },
            IntentType.REMINDER: {
                "create": ["datetime", "topic"],
                "read": [],
                "update": ["datetime", "topic"],
                "delete": ["topic"],
                "list": []
            },
            IntentType.WEATHER: {
                "current": [],
                "forecast": ["datetime"],
                "conditions": ["location"]
            },
            IntentType.NEWS: {
                "headlines": [],
                "search": ["topic"],
                "category": ["topic"]
            },
            IntentType.SEARCH: {
                "web_search": ["topic"],
                "information": ["topic"],
                "lookup": ["topic"]
            }
        }
        
        return requirements.get(intent_type, {}).get(action, [])

# Global instance
intent_recognizer = IntentRecognizer()
