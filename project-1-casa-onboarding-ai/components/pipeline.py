import os
import json
from crewai import Agent, Task, Crew, Process, LLM
from components.database import OnboardingVectorStore

class CASAOnboardingEngine:
    def __init__(self):
        self.db = OnboardingVectorStore()
        
        # FIX: Switched to active 'gemini-2.5-flash' model and wrapped it in the CrewAI LLM class
        self.llm = LLM(
            model="gemini/gemini-2.5-flash",
            api_key=os.environ.get("GEMINI_API_KEY")
        )

    def run_onboarding_pipeline(self, uploaded_document_text: str, human_override_notes: str = "") -> dict:
        context_rules = self.db.query_compliance_rules(uploaded_document_text, top_k=2)

        scrutiny_agent = Agent(
            role="Data Scrutiny Specialist",
            goal="Accurately extract structural corporate profile variables from raw documentation text packages.",
            backstory="An elite document parsing analyst capable of structured entity variable isolation without introducing text hallucinations.",
            verbose=True,
            llm=self.llm
        )

        compliance_agent = Agent(
            role="Corporate Compliance Audit Expert",
            goal="Cross-examine extracted corporate structural variables against active regulatory rule sets.",
            backstory="A meticulous legal auditor checking corporate metadata alignment against structural policy rules. Flags discrepancies instantly.",
            verbose=True,
            llm=self.llm
        )

        extraction_task = Task(
            description=f"""
            Parse the following raw text content package pulled directly from customer registration uploads:
            ---
            {uploaded_document_text}
            ---
            Isolate and construct a JSON list containing: Legal Entity Name, Incorporation IDs, and Key Executives holding over 25% control shares.
            """,
            expected_output="A structured raw data key-value distillation summary.",
            agent=scrutiny_agent
        )

        audit_task = Task(
            description=f"""
            Review the extracted entity metadata produced from the document scrutiny phase.
            Evaluate its explicit operational alignment against these strict structural regulatory rules:
            ---
            {context_rules}
            ---
            
            Current User-Assigned Operational Override Notes: "{human_override_notes}"
            
            If critical entity elements (such as explicit UBO identities or valid signing authority records) are missing, you must flag the application risk status as 'VERIFICATION_HOLD'.
            """,
            expected_output="""A clean JSON document structure containing exactly:
            {{
               "entity_name": "Isolated Name string",
               "verification_status": "APPROVED" or "VERIFICATION_HOLD",
               "compliance_gaps": ["List specific missing elements or string description"],
               "regulatory_reference_applied": "Snippet of section rule reviewed"
            }}""",
            agent=compliance_agent
        )

        crew = Crew(
            agents=[scrutiny_agent, compliance_agent],
            tasks=[extraction_task, audit_task],
            process=Process.sequential,
            verbose=True
        )

        raw_result = crew.kickoff()
        
        # Clean potential markdown block tags to safely parse the output string as dictionary
        cleaned_json = str(raw_result).replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned_json)
        except Exception:
            return {
                "entity_name": "Extraction Failure",
                "verification_status": "VERIFICATION_HOLD",
                "compliance_gaps": ["System failed to synthesize a clean data structure payload."],
                "regulatory_reference_applied": "Internal Error"
            }