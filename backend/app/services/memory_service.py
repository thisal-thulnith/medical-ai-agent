"""
Memory Service using ChromaDB for long-term patient context
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings as app_settings


class MemoryService:
    """
    Manages long-term memory for each user using vector database
    """

    def __init__(self):
        # Initialize ChromaDB client (persistent storage)
        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )

        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=app_settings.OPENAI_API_KEY
        )

        # Create or get collections
        self.medical_history_collection = self.client.get_or_create_collection(
            name="medical_history",
            metadata={"description": "User medical history and important health facts"}
        )

        self.conversation_collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"description": "Past conversation context"}
        )

    def add_medical_fact(self, user_id: int, fact: str, metadata: Dict[str, Any] = None):
        """
        Add an important medical fact to long-term memory

        Args:
            user_id: User ID
            fact: Medical fact or information
            metadata: Additional metadata (date, source, etc.)
        """
        embedding = self.embeddings.embed_query(fact)

        meta = metadata or {}
        meta["user_id"] = user_id

        self.medical_history_collection.add(
            ids=[f"user_{user_id}_fact_{hash(fact)}"],
            embeddings=[embedding],
            documents=[fact],
            metadatas=[meta]
        )

    def add_conversation_memory(self, user_id: int, conversation_summary: str,
                                conversation_id: int, metadata: Dict[str, Any] = None):
        """
        Store conversation summary for future context retrieval

        Args:
            user_id: User ID
            conversation_summary: Summary of the conversation
            conversation_id: Conversation ID
            metadata: Additional metadata
        """
        embedding = self.embeddings.embed_query(conversation_summary)

        meta = metadata or {}
        meta.update({
            "user_id": user_id,
            "conversation_id": conversation_id
        })

        self.conversation_collection.add(
            ids=[f"user_{user_id}_conv_{conversation_id}"],
            embeddings=[embedding],
            documents=[conversation_summary],
            metadatas=[meta]
        )

    def retrieve_relevant_context(self, user_id: int, query: str, n_results: int = 5) -> List[str]:
        """
        Retrieve relevant context from memory based on current query

        Args:
            user_id: User ID
            query: Current user query
            n_results: Number of results to retrieve

        Returns:
            List of relevant context strings
        """
        query_embedding = self.embeddings.embed_query(query)

        # Search medical history
        medical_results = self.medical_history_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"user_id": user_id}
        )

        # Search past conversations
        conversation_results = self.conversation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"user_id": user_id}
        )

        # Combine results
        context = []
        if medical_results["documents"]:
            context.extend(medical_results["documents"][0])
        if conversation_results["documents"]:
            context.extend(conversation_results["documents"][0])

        return context

    def get_user_memory_summary(self, user_id: int) -> Dict[str, List[str]]:
        """
        Get all stored memories for a user

        Args:
            user_id: User ID

        Returns:
            Dict with medical_facts and conversations
        """
        # Get all medical facts
        medical_facts = self.medical_history_collection.get(
            where={"user_id": user_id}
        )

        # Get all conversation summaries
        conversations = self.conversation_collection.get(
            where={"user_id": user_id}
        )

        return {
            "medical_facts": medical_facts.get("documents", []),
            "conversations": conversations.get("documents", [])
        }

    def delete_user_memory(self, user_id: int):
        """
        Delete all memory for a user (for privacy/GDPR compliance)

        Args:
            user_id: User ID
        """
        # Delete from medical history
        medical_ids = self.medical_history_collection.get(
            where={"user_id": user_id}
        ).get("ids", [])

        if medical_ids:
            self.medical_history_collection.delete(ids=medical_ids)

        # Delete from conversations
        conv_ids = self.conversation_collection.get(
            where={"user_id": user_id}
        ).get("ids", [])

        if conv_ids:
            self.conversation_collection.delete(ids=conv_ids)
