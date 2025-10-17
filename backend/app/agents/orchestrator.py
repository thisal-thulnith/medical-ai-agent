"""
Main LangGraph Orchestrator for Medical AI Agent
"""
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.agents.state import AgentState, IntentType
from app.core.config import settings
import json


class MedicalAgentOrchestrator:
    """
    Master orchestrator that routes user messages to specialized agents
    using LangGraph
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Fast and cost-effective
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )
        self.llm_smart = ChatOpenAI(
            model="gpt-4o",  # For complex medical reasoning
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("symptom_agent", self._symptom_agent)
        workflow.add_node("medication_agent", self._medication_agent)
        workflow.add_node("report_agent", self._report_agent)
        workflow.add_node("diagnosis_agent", self._diagnosis_agent)
        workflow.add_node("lifestyle_agent", self._lifestyle_agent)
        workflow.add_node("emergency_agent", self._emergency_agent)
        workflow.add_node("general_agent", self._general_agent)
        workflow.add_node("data_logger", self._data_logger)
        workflow.add_node("response_generator", self._response_generator)

        # Define edges
        workflow.set_entry_point("classify_intent")

        workflow.add_edge("classify_intent", "retrieve_context")

        # Conditional routing based on intent
        workflow.add_conditional_edges(
            "retrieve_context",
            self._route_by_intent,
            {
                IntentType.SYMPTOM_ANALYSIS: "symptom_agent",
                IntentType.MEDICATION_QUERY: "medication_agent",
                IntentType.MEDICATION_INTERACTION: "medication_agent",
                IntentType.REPORT_ANALYSIS: "report_agent",
                IntentType.DIAGNOSIS_ASSISTANCE: "diagnosis_agent",
                IntentType.LIFESTYLE_ADVICE: "lifestyle_agent",
                IntentType.EMERGENCY: "emergency_agent",
                "default": "general_agent",
            }
        )

        # All agents go to data logger
        for agent in ["symptom_agent", "medication_agent", "report_agent",
                      "diagnosis_agent", "lifestyle_agent", "emergency_agent", "general_agent"]:
            workflow.add_edge(agent, "data_logger")

        workflow.add_edge("data_logger", "response_generator")
        workflow.add_edge("response_generator", END)

        return workflow.compile()

    def _classify_intent(self, state: AgentState) -> AgentState:
        """Classify user's intent"""
        user_message = state["user_message"]

        # Check if message contains uploaded report indicators
        has_report_id = "Report ID:" in user_message or "report id" in user_message.lower()
        has_uploaded_reports = state.get("user_context", {}).get("uploaded_reports")

        # If user has uploaded reports and message mentions them, classify as report_analysis
        if has_report_id or (has_uploaded_reports and ("analyze" in user_message.lower() or "report" in user_message.lower())):
            state["intent"] = "report_analysis"
            state["extracted_entities"] = {}
            state["agent_path"] = ["intent_classifier"]
            return state

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intent classifier for a medical AI assistant that ONLY handles medical and health topics.

Classify the user's message into ONE of these intents:
- symptom_analysis: User describes symptoms or health issues
- health_tracking: User wants to log health data (vitals, weight, etc.)
- medication_query: Questions about medications
- medication_interaction: Checking drug interactions
- report_analysis: User uploaded or mentions medical reports
- diagnosis_assistance: User wants help understanding a diagnosis
- treatment_planning: Questions about treatment options
- lifestyle_advice: Diet, exercise, wellness questions
- emergency: Urgent medical situation
- general_medical_query: General medical questions (including greetings if medical context)
- data_retrieval: User wants to see their health data
- non_medical_query: Questions NOT related to health/medicine (weather, sports, coding, etc.)

IMPORTANT: If the question is clearly non-medical, classify as "non_medical_query"

Respond with ONLY the intent name and a JSON object of extracted entities.

Examples:
User: "I have a headache and fever"
Intent: symptom_analysis
Entities: {{"symptoms": ["headache", "fever"]}}

User: "What medications should I take for diabetes?"
Intent: medication_query
Entities: {{"condition": "diabetes"}}

User: "Show me my blood pressure readings"
Intent: data_retrieval
Entities: {{"data_type": "blood_pressure"}}
"""),
            ("user", "{message}")
        ])

        response = self.llm.invoke(prompt.format_messages(message=user_message))
        content = response.content.strip()

        # Parse intent and entities
        lines = content.split('\n')
        intent = lines[0].replace("Intent:", "").strip()

        entities = {}
        for line in lines[1:]:
            if line.startswith("Entities:"):
                try:
                    entities = json.loads(line.replace("Entities:", "").strip())
                except:
                    pass

        state["intent"] = intent
        state["extracted_entities"] = entities
        state["agent_path"] = ["intent_classifier"]

        return state

    def _retrieve_context(self, state: AgentState) -> AgentState:
        """Retrieve user's medical context from memory/database"""
        # This will be populated by the API endpoint with user's medical data
        # For now, just mark that we've retrieved context
        state["agent_path"].append("context_retriever")
        return state

    def _route_by_intent(self, state: AgentState) -> str:
        """Route to appropriate agent based on intent"""
        intent = state.get("intent", "")

        if intent in [IntentType.SYMPTOM_ANALYSIS, IntentType.HEALTH_TRACKING]:
            return IntentType.SYMPTOM_ANALYSIS
        elif intent in [IntentType.MEDICATION_QUERY, IntentType.MEDICATION_INTERACTION]:
            return intent
        elif intent == IntentType.EMERGENCY:
            return IntentType.EMERGENCY
        elif intent == IntentType.REPORT_ANALYSIS:
            return IntentType.REPORT_ANALYSIS
        elif intent == IntentType.DIAGNOSIS_ASSISTANCE:
            return IntentType.DIAGNOSIS_ASSISTANCE
        elif intent == IntentType.LIFESTYLE_ADVICE:
            return IntentType.LIFESTYLE_ADVICE
        else:
            return "default"

    def _symptom_agent(self, state: AgentState) -> AgentState:
        """Analyze symptoms and provide guidance"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a medical symptom analyzer. Analyze the user's symptoms and:
1. Extract structured symptom data (name, severity, body part, duration)
2. Assess severity level (mild, moderate, severe, critical)
3. Suggest possible causes (differential diagnosis)
4. Recommend appropriate actions
5. Identify red flags that need immediate attention

User Context:
- Medical History: {medical_history}
- Current Medications: {medications}
- Known Allergies: {allergies}
- Age & Gender: {demographics}

Be empathetic but thorough. If symptoms are concerning, recommend seeing a doctor.

Output Format:
Analysis: [your analysis]
Extracted Data: {{"symptoms": [{{"name": "", "severity": "", "body_part": "", "duration_days": }}]}}
Recommendations: [your recommendations]
"""),
            ("user", "{message}")
        ])

        context = state.get("user_context", {})
        response = self.llm_smart.invoke(prompt.format_messages(
            message=state["user_message"],
            medical_history=context.get("conditions", []),
            medications=context.get("medications", []),
            allergies=context.get("allergies", []),
            demographics=context.get("demographics", {})
        ))

        state["agent_responses"].append(response.content)
        state["agent_path"].append("symptom_agent")

        # Extract structured data
        try:
            # Parse the "Extracted Data:" section
            content = response.content
            if "Extracted Data:" in content:
                data_section = content.split("Extracted Data:")[1].split("Recommendations:")[0]
                extracted = json.loads(data_section.strip())
                state["data_to_save"]["symptoms"] = extracted.get("symptoms", [])
        except Exception as e:
            print(f"Error extracting symptom data: {e}")

        return state

    def _medication_agent(self, state: AgentState) -> AgentState:
        """Handle medication queries and interactions with advanced API integration"""
        # Import here to avoid circular imports
        from app.services.external_apis import MedicalAPIService
        import asyncio

        api_service = MedicalAPIService()
        context = state.get("user_context", {})
        extracted_entities = state.get("extracted_entities", {})

        # Check if user is asking about a specific medication
        medication_query = None
        if "medication" in extracted_entities:
            medication_query = extracted_entities["medication"]
        elif "condition" in extracted_entities:
            condition_query = extracted_entities["condition"]
        else:
            # Try to extract medication name from message
            words = state["user_message"].lower().split()
            # Simple heuristic - capitalize words that might be drug names
            potential_meds = [w for w in state["user_message"].split() if w[0].isupper() and len(w) > 3]
            if potential_meds:
                medication_query = potential_meds[0]

        # Gather medication information from APIs
        api_data = {}
        if medication_query:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, we can't use run_until_complete
                    # Use synchronous approach or schedule as task
                    pass
                else:
                    # Get comprehensive medication info
                    user_allergies = [a.get("allergen", "") for a in context.get("allergies", [])]
                    user_conditions = [c.get("name", "") for c in context.get("conditions", [])]

                    drug_info = loop.run_until_complete(api_service.search_drug_info(medication_query))
                    rxnorm_info = loop.run_until_complete(api_service.search_rxnorm(medication_query))
                    safety_analysis = loop.run_until_complete(
                        api_service.analyze_medication_safety(
                            medication_query,
                            user_allergies,
                            user_conditions
                        )
                    )

                    api_data = {
                        "fda_info": drug_info,
                        "rxnorm_info": rxnorm_info,
                        "safety_analysis": safety_analysis
                    }
            except Exception as e:
                print(f"Error fetching medication data: {e}")
                api_data = {"error": str(e)}

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an advanced medication specialist AI with access to comprehensive drug databases.

Help users with:
1. Detailed medication information (uses, dosage, side effects, warnings)
2. Drug interaction checking using RxNorm and FDA databases
3. Medication safety analysis based on user's allergies and conditions
4. Alternative medications and treatment options
5. Medication tracking and reminders

User's Current Medications: {current_medications}
Known Allergies: {allergies}
Medical Conditions: {conditions}

External API Data Available:
{api_data}

Use the API data to provide specific, evidence-based information. Always include:
- Safety warnings specific to this user
- Drug interaction alerts
- Contraindications with user's conditions
- Allergy warnings

CRITICAL SAFETY RULES:
1. If API data shows HIGH_RISK safety score, strongly warn the user
2. If allergy warnings are present, advise DO NOT TAKE
3. Always recommend consulting a doctor or pharmacist before starting any medication
4. Provide FDA warnings and adverse reactions

If the user wants to log a new medication, extract:
{{"medications": [{{"name": "", "dosage": "", "frequency": "", "purpose": ""}}]}}

Be thorough like a human doctor would be - consider all factors and explain your reasoning.
"""),
            ("user", "{message}")
        ])

        response = self.llm_smart.invoke(prompt.format_messages(
            message=state["user_message"],
            current_medications=context.get("medications", []),
            allergies=context.get("allergies", []),
            conditions=context.get("conditions", []),
            api_data=json.dumps(api_data, indent=2) if api_data else "No API data available"
        ))

        state["agent_responses"].append(response.content)
        state["agent_path"].append("medication_agent")

        return state

    def _report_agent(self, state: AgentState) -> AgentState:
        """Analyze medical reports"""
        context = state.get("user_context", {})
        uploaded_reports = context.get("uploaded_reports", [])

        if not uploaded_reports:
            state["agent_responses"].append(
                "I can help analyze your medical reports. Please upload the report file, "
                "and I'll extract key findings and explain them in simple terms."
            )
            state["agent_path"].append("report_agent")
            return state

        # Analyze each uploaded report
        for report in uploaded_reports:
            extracted_text = report.get("extracted_text", "")
            structured_data = report.get("structured_data", {})
            report_type = report.get("type", "unknown")
            file_name = report.get("file_name", "unknown")

            # Build context for analysis
            analysis_context = f"""
            Report Type: {report_type}
            File Name: {file_name}

            Extracted Text:
            {extracted_text}

            Structured Data:
            {structured_data}
            """

            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a medical report analysis expert. Analyze the provided medical report and provide:

1. Summary of Key Findings:
   - What type of test or report is this?
   - What are the main results?

2. Interpretation:
   - What do these results mean?
   - Are there any abnormal values?
   - How do they compare to normal ranges?

3. Clinical Significance:
   - What might these results indicate?
   - Are there any concerning findings?
   - What follow-up might be needed?

4. Plain Language Explanation:
   - Explain complex medical terms
   - Help the patient understand their report

User Context:
Age: {age}
Gender: {gender}
Medical Conditions: {conditions}
Current Medications: {medications}

IMPORTANT: Be thorough but clear. Avoid using ** markdown bold formatting."""),
                ("user", "{report_content}")
            ])

            chain = prompt | self.llm
            response = chain.invoke({
                "report_content": analysis_context,
                "age": context.get("demographics", {}).get("age", "unknown"),
                "gender": context.get("demographics", {}).get("gender", "unknown"),
                "conditions": ", ".join([c.get("name", "") for c in context.get("conditions", [])]),
                "medications": ", ".join([m.get("name", "") for m in context.get("medications", [])])
            })

            state["agent_responses"].append(response.content)

        state["agent_path"].append("report_agent")
        return state

    def _diagnosis_agent(self, state: AgentState) -> AgentState:
        """Assist with understanding diagnoses using advanced medical reasoning"""
        from app.services.external_apis import MedicalAPIService
        import asyncio

        api_service = MedicalAPIService()
        context = state.get("user_context", {})

        # Extract symptoms and conditions from user context
        symptoms = []
        if "recent_symptoms" in context:
            symptoms = [s.get("symptom", "") for s in context.get("recent_symptoms", [])]

        extracted_entities = state.get("extracted_entities", {})
        if "symptoms" in extracted_entities:
            symptoms.extend(extracted_entities["symptoms"])

        # Get medical literature and ICD-10 codes
        api_data = {}
        if symptoms:
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    # Search for related medical literature
                    search_query = " ".join(symptoms[:3])  # Use top 3 symptoms
                    literature = loop.run_until_complete(
                        api_service.search_medical_literature(search_query, max_results=5)
                    )

                    # Get ICD-10 codes for symptoms
                    icd_codes = []
                    for symptom in symptoms[:3]:
                        icd_result = loop.run_until_complete(api_service.get_icd10_code(symptom))
                        if "results" in icd_result:
                            icd_codes.extend(icd_result["results"][:2])

                    api_data = {
                        "literature": literature,
                        "icd_codes": icd_codes
                    }
            except Exception as e:
                print(f"Error fetching diagnosis data: {e}")
                api_data = {"error": str(e)}

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an advanced medical diagnostic assistant with access to medical literature and ICD-10 databases.

Provide comprehensive analysis including:

1. **Differential Diagnosis**: List possible conditions that match the symptoms
   - Rank by likelihood based on symptom pattern
   - Consider user's medical history and risk factors

2. **Clinical Reasoning**: Explain your diagnostic thinking
   - Which symptoms point to which conditions
   - Red flags that need immediate attention
   - Benign vs serious possibilities

3. **Evidence-Based Information**: Use provided medical literature
   - Reference recent research
   - Cite ICD-10 codes where relevant

4. **Recommended Actions**:
   - What tests/examinations would help confirm diagnosis
   - When to seek immediate medical care
   - Specialists to consult

5. **Patient Education**:
   - Explain conditions in simple terms
   - What to expect and monitor
   - Lifestyle factors that may help

User's Profile:
- Symptoms: {symptoms}
- Medical History: {medical_history}
- Current Medications: {medications}
- Recent Vitals: {vitals}

Medical Literature & ICD-10 Data:
{api_data}

IMPORTANT:
- This is differential diagnosis assistance, NOT a definitive diagnosis
- Always emphasize the need for proper medical examination
- Be thorough like a human doctor conducting differential diagnosis
- Consider both common and rare possibilities
- Flag urgent symptoms clearly

Be empathetic and thorough in your analysis.
"""),
            ("user", "{message}")
        ])

        response = self.llm_smart.invoke(prompt.format_messages(
            message=state["user_message"],
            symptoms=symptoms,
            medical_history=context.get("conditions", []),
            medications=context.get("medications", []),
            vitals=context.get("recent_vitals", []),
            api_data=json.dumps(api_data, indent=2) if api_data else "No external data available"
        ))

        state["agent_responses"].append(response.content)
        state["agent_path"].append("diagnosis_agent")
        return state

    def _lifestyle_agent(self, state: AgentState) -> AgentState:
        """Provide lifestyle and wellness advice"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a health and wellness coach providing evidence-based lifestyle advice.

Areas you can help with:
- Nutrition and diet planning
- Exercise recommendations
- Sleep hygiene
- Stress management
- Weight management
- Preventive health

User Info:
- Age: {age}
- Medical Conditions: {conditions}
- Current Medications: {medications}
- Health Goals: {goals}

Provide personalized, actionable advice. Consider the user's medical conditions and limitations.
"""),
            ("user", "{message}")
        ])

        context = state.get("user_context", {})
        response = self.llm.invoke(prompt.format_messages(
            message=state["user_message"],
            age=context.get("demographics", {}).get("age", "not specified"),
            conditions=context.get("conditions", []),
            medications=context.get("medications", []),
            goals=context.get("health_goals", [])
        ))

        state["agent_responses"].append(response.content)
        state["agent_path"].append("lifestyle_agent")
        return state

    def _emergency_agent(self, state: AgentState) -> AgentState:
        """Handle emergency situations"""
        emergency_response = """
🚨 EMERGENCY DETECTED 🚨

If you are experiencing a medical emergency, please:
1. CALL 911 (or your local emergency number) IMMEDIATELY
2. Do not wait for online medical advice
3. If someone is with you, have them call while you stay with the patient

Common emergencies that need immediate care:
- Chest pain or pressure
- Difficulty breathing
- Severe bleeding
- Loss of consciousness
- Stroke symptoms (facial drooping, arm weakness, speech difficulty)
- Severe allergic reaction
- Severe burns
- Severe head injury

If this is not an emergency, please describe your symptoms and I can help assess the situation.
"""
        state["agent_responses"].append(emergency_response)
        state["agent_path"].append("emergency_agent")
        return state

    def _general_agent(self, state: AgentState) -> AgentState:
        """Handle general medical queries and conversations"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a specialized medical AI assistant. You ONLY answer health and medical-related questions.

IMPORTANT RESTRICTION: You are programmed to discuss ONLY medical and health topics including:
- Symptoms, diagnoses, and medical conditions
- Medications and treatments
- Medical reports and test results
- Health tracking (vitals, nutrition, exercise)
- Preventive care and wellness
- Medical terminology and education
- Mental health and well-being

For NON-MEDICAL questions, you MUST politely decline and redirect:
"I'm a medical AI assistant and I can only help with health and medical-related questions. Please ask me about your health concerns, symptoms, medications, or medical reports."

Previous conversation context: {chat_history}

Always be:
- Empathetic and supportive
- Clear and informative
- Honest about limitations
- Encouraging of professional medical consultation when appropriate
- STRICT about only answering medical questions
"""),
            ("user", "{message}")
        ])

        response = self.llm.invoke(prompt.format_messages(
            message=state["user_message"],
            chat_history=state.get("chat_history", [])[-10:]  # Last 10 messages
        ))

        state["agent_responses"].append(response.content)
        state["agent_path"].append("general_agent")
        return state

    def _data_logger(self, state: AgentState) -> AgentState:
        """Extract and prepare data for logging to database"""
        # This node prepares structured data extracted from the conversation
        # The actual database saving happens in the API endpoint
        state["agent_path"].append("data_logger")

        if "data_to_save" not in state:
            state["data_to_save"] = {}

        return state

    def _format_response(self, text: str) -> str:
        """Format response text for better readability"""
        import re

        # Remove markdown bold ** but keep the text
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)

        # Remove single * emphasis
        text = re.sub(r'(?<!\*)\*(?!\*)([^\*]+)\*(?!\*)', r'\1', text)

        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Clean up spaces
        text = re.sub(r'  +', ' ', text)

        return text.strip()

    def _response_generator(self, state: AgentState) -> AgentState:
        """Generate final response from all agent outputs"""
        # Combine all agent responses
        all_responses = state.get("agent_responses", [])

        if len(all_responses) == 1:
            raw_response = all_responses[0]
        else:
            # If multiple agents contributed, synthesize their responses
            raw_response = "\n\n".join(all_responses)

        # Format the response to remove markdown and improve readability
        state["final_response"] = self._format_response(raw_response)

        state["agent_path"].append("response_generator")
        return state

    async def process_message(self, user_message: str, user_id: int,
                              conversation_id: int = None,
                              user_context: Dict[str, Any] = None,
                              chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process a user message through the LangGraph workflow

        Returns:
            Dict with final_response, data_to_save, and metadata
        """
        initial_state: AgentState = {
            "user_message": user_message,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "chat_history": chat_history or [],
            "user_context": user_context or {},
            "intent": None,
            "extracted_entities": {},
            "agent_path": [],
            "agent_responses": [],
            "final_response": "",
            "data_to_save": {},
            "actions": [],
            "external_data": {},
            "metadata": {}
        }

        # Run through the graph
        final_state = await self.graph.ainvoke(initial_state)

        return {
            "response": final_state["final_response"],
            "intent": final_state["intent"],
            "data_to_save": final_state["data_to_save"],
            "agent_path": final_state["agent_path"],
            "metadata": final_state["metadata"]
        }
