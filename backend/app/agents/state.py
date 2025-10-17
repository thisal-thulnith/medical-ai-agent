"""
LangGraph State Definitions for Medical AI Agent
"""
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from operator import add


class AgentState(TypedDict):
    """
    State that flows through the LangGraph workflow
    """
    # User input and conversation
    user_message: str
    user_id: int
    conversation_id: Optional[int]

    # Conversation history for context
    chat_history: List[Dict[str, str]]

    # User's medical context
    user_context: Dict[str, Any]  # Medical history, conditions, meds, allergies

    # Intent classification
    intent: Optional[str]  # symptom_analysis, medication_query, report_analysis, etc.

    # Extracted entities
    extracted_entities: Dict[str, Any]

    # Agent routing
    agent_path: List[str]  # Track which agents processed this

    # Generated responses
    agent_responses: Annotated[List[str], add]  # Accumulate responses from multiple agents

    # Final response
    final_response: str

    # Structured data to save
    data_to_save: Dict[str, Any]  # Symptoms, vitals, medications extracted

    # Actions to take
    actions: List[Dict[str, Any]]  # e.g., [{"type": "reminder", "data": {...}}]

    # External API calls results
    external_data: Dict[str, Any]

    # Metadata
    metadata: Dict[str, Any]


class IntentType:
    """Intent classification types"""
    SYMPTOM_ANALYSIS = "symptom_analysis"
    HEALTH_TRACKING = "health_tracking"
    MEDICATION_QUERY = "medication_query"
    MEDICATION_INTERACTION = "medication_interaction"
    REPORT_ANALYSIS = "report_analysis"
    DIAGNOSIS_ASSISTANCE = "diagnosis_assistance"
    TREATMENT_PLANNING = "treatment_planning"
    LIFESTYLE_ADVICE = "lifestyle_advice"
    EMERGENCY = "emergency"
    GENERAL_MEDICAL_QUERY = "general_medical_query"
    SMALL_TALK = "small_talk"
    DATA_RETRIEVAL = "data_retrieval"  # User wants to see their data
