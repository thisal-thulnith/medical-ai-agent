"""
Chat API endpoints - Main interface for medical AI agent
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, date

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, Message, MessageRole
from app.models.health_data import Symptom, VitalSign, Medication, SeverityLevel, VitalSignType, MedicalReport
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage, ConversationResponse, ConversationDetail
from app.agents.orchestrator import MedicalAgentOrchestrator
from app.services.memory_service import MemoryService
from app.services.external_apis import MedicalAPIService
import re

router = APIRouter(prefix="/chat", tags=["Chat"])

# Initialize services
agent_orchestrator = MedicalAgentOrchestrator()
memory_service = MemoryService()
api_service = MedicalAPIService()


def extract_report_ids_from_message(message: str) -> List[int]:
    """
    Extract report IDs from user message
    Example: "Report ID: 1" or "report id 1" -> [1]
    """
    pattern = r'Report\s+ID:\s*(\d+)'
    matches = re.findall(pattern, message, re.IGNORECASE)
    return [int(m) for m in matches]


def get_user_context(db: Session, user: User) -> Dict[str, Any]:
    """
    Gather user's medical context for the AI agent

    Args:
        db: Database session
        user: Current user

    Returns:
        Dict with user's medical context
    """
    # Get user's medical conditions
    conditions = db.query.filter_by(user_id=user.id).all() if hasattr(db.query, 'filter_by') else []

    # Get active medications
    medications = db.query(Medication).filter(
        Medication.user_id == user.id,
        Medication.is_active == 1
    ).all()

    # Get allergies
    allergies = user.allergies

    # Get recent symptoms (last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_symptoms = db.query(Symptom).filter(
        Symptom.user_id == user.id,
        Symptom.logged_at >= thirty_days_ago
    ).all()

    # Get recent vital signs
    recent_vitals = db.query(VitalSign).filter(
        VitalSign.user_id == user.id,
        VitalSign.recorded_at >= thirty_days_ago
    ).order_by(VitalSign.recorded_at.desc()).limit(10).all()

    return {
        "demographics": {
            "age": (date.today() - user.date_of_birth).days // 365 if user.date_of_birth else None,
            "gender": user.gender.value if user.gender else None,
            "blood_type": user.blood_type
        },
        "conditions": [
            {
                "name": c.condition_name,
                "status": c.status,
                "diagnosed_date": c.diagnosed_date.isoformat() if c.diagnosed_date else None
            }
            for c in user.health_conditions
        ],
        "medications": [
            {
                "name": m.name,
                "dosage": m.dosage,
                "frequency": m.frequency,
                "purpose": m.purpose
            }
            for m in medications
        ],
        "allergies": [
            {
                "allergen": a.allergen,
                "severity": a.severity.value,
                "reaction": a.reaction
            }
            for a in allergies
        ],
        "recent_symptoms": [
            {
                "symptom": s.symptom_name,
                "severity": s.severity.value if s.severity else None,
                "date": s.logged_at.isoformat()
            }
            for s in recent_symptoms
        ],
        "recent_vitals": [
            {
                "type": v.type.value,
                "value": v.value,
                "unit": v.unit,
                "date": v.recorded_at.isoformat()
            }
            for v in recent_vitals
        ]
    }


def save_extracted_data(db: Session, user_id: int, conversation_id: int, data: Dict[str, Any]):
    """
    Save extracted health data from conversation to database

    Args:
        db: Database session
        user_id: User ID
        conversation_id: Conversation ID
        data: Extracted data from AI agent
    """
    # Save symptoms
    if "symptoms" in data:
        for symptom_data in data["symptoms"]:
            symptom = Symptom(
                user_id=user_id,
                conversation_id=conversation_id,
                symptom_name=symptom_data.get("name", ""),
                severity=SeverityLevel(symptom_data["severity"]) if symptom_data.get("severity") else None,
                body_part=symptom_data.get("body_part"),
                description=symptom_data.get("description"),
                duration_days=symptom_data.get("duration_days")
            )
            db.add(symptom)

    # Save vital signs
    if "vital_signs" in data:
        for vital_data in data["vital_signs"]:
            vital = VitalSign(
                user_id=user_id,
                conversation_id=conversation_id,
                type=VitalSignType(vital_data["type"]),
                value=vital_data["value"],
                unit=vital_data["unit"],
                notes=vital_data.get("notes")
            )
            db.add(vital)

    # Save medications
    if "medications" in data:
        for med_data in data["medications"]:
            medication = Medication(
                user_id=user_id,
                conversation_id=conversation_id,
                name=med_data["name"],
                dosage=med_data["dosage"],
                frequency=med_data["frequency"],
                start_date=date.today(),
                purpose=med_data.get("purpose")
            )
            db.add(medication)

    db.commit()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI medical agent

    The agent will:
    1. Classify intent
    2. Retrieve relevant context
    3. Route to specialized agents
    4. Extract structured health data
    5. Generate response
    6. Save data to database
    """
    # Get or create conversation
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:50] + "..." if len(request.message) > 50 else request.message
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.user,
        content=request.message
    )
    db.add(user_message)
    db.commit()

    # Get conversation history if requested
    chat_history = []
    if request.include_history:
        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.timestamp.desc()).limit(20).all()

        chat_history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in reversed(messages)
        ]

    # Get user's medical context
    user_context = get_user_context(db, current_user)

    # Check if message contains report IDs and fetch report data
    report_ids = extract_report_ids_from_message(request.message)
    if report_ids:
        reports_data = []
        for report_id in report_ids:
            report = db.query(MedicalReport).filter(
                MedicalReport.id == report_id,
                MedicalReport.user_id == current_user.id
            ).first()
            if report:
                reports_data.append({
                    "id": report.id,
                    "type": report.report_type.value,
                    "file_name": report.file_name,
                    "extracted_text": report.parsed_data.get("text", "") if report.parsed_data else "",
                    "structured_data": report.parsed_data.get("structured_data", {}) if report.parsed_data else {},
                    "ai_analysis": report.ai_analysis,
                    "report_date": report.report_date.isoformat() if report.report_date else None
                })
        user_context["uploaded_reports"] = reports_data

    # Retrieve relevant memory
    relevant_memory = memory_service.retrieve_relevant_context(
        user_id=current_user.id,
        query=request.message,
        n_results=3
    )
    user_context["memory"] = relevant_memory

    # Process message through LangGraph agent
    result = await agent_orchestrator.process_message(
        user_message=request.message,
        user_id=current_user.id,
        conversation_id=conversation.id,
        user_context=user_context,
        chat_history=chat_history
    )

    # Save assistant response
    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.assistant,
        content=result["response"],
        meta_data={
            "intent": result["intent"],
            "agent_path": result["agent_path"]
        }
    )
    db.add(assistant_message)

    # Save extracted health data
    if result.get("data_to_save"):
        save_extracted_data(db, current_user.id, conversation.id, result["data_to_save"])

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(assistant_message)

    # Store conversation in memory for future context
    if len(chat_history) > 0 and len(chat_history) % 10 == 0:
        # Every 10 messages, create a summary for long-term memory
        summary = f"User discussed: {result['intent']} - Key points: {request.message[:200]}"
        memory_service.add_conversation_memory(
            user_id=current_user.id,
            conversation_summary=summary,
            conversation_id=conversation.id
        )

    return ChatResponse(
        conversation_id=conversation.id,
        message=ChatMessage(
            role=assistant_message.role,
            content=assistant_message.content,
            timestamp=assistant_message.timestamp,
            meta_data=assistant_message.meta_data
        ),
        extracted_data=result.get("data_to_save")
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all conversations for the current user
    """
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()

    response = []
    for conv in conversations:
        last_message = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.timestamp.desc()).first()

        response.append(ConversationResponse(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(conv.messages),
            last_message=last_message.content[:100] if last_message else None
        ))

    return response


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation_detail(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed conversation with all messages
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    messages = [ChatMessage.from_orm(msg) for msg in conversation.messages]

    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        messages=messages
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a conversation and all its messages
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    db.delete(conversation)
    db.commit()

    return None
