import os
from crewai import Agent, Task, Crew, Process, LLM

def run_rfp_pipeline(company_profile_text, rfp_requirements_text):
    # Initializes the verified Gemini 2.5 Flash model layout
    gemini_llm = LLM(
        model="gemini/gemini-2.5-flash",
        api_key=os.environ.get("GOOGLE_API_KEY")
    )

    # Agent 1: Deep Compliance Auditor
    compliance_analyst = Agent(
        role="Lead Enterprise Compliance & Procurement Auditor",
        goal="Deconstruct unstructured RFP frameworks into explicit, binding technical and legal demands.",
        backstory="An elite procurement architect who spent decades auditing complex enterprise bids. You instantly separate legal fluff from core operational deliverables.",
        verbose=True,
        allow_delegation=False,
        llm=gemini_llm
    )

    # Agent 2: High-Stakes Technical Writer
    proposal_writer = Agent(
        role="Principal B2B Solutions Architect & Proposal Writer",
        goal="Synthesize flawless, data-backed technical bids that map corporate capabilities to client demands.",
        backstory="A high-impact executive writer skilled at aligning company performance history, technical stacks, and security compliance directly with procurement checklists without introducing hallucinations.",
        verbose=True,
        allow_delegation=False,
        llm=gemini_llm
    )

    # Task 1: Semantic Parsing & Requirements Extraction
    extraction_task = Task(
        description=f"""
        Analyze the incoming targeted Request for Proposal (RFP) technical specification document:
        ---
        {rfp_requirements_text}
        ---
        Generate an exhaustive operational audit checklist. Extract all mandatory compliance standards, technical performance milestones, and explicit business objectives.
        """,
        expected_output="An organized markdown summary detailing critical evaluation criteria and mandatory client milestones.",
        agent=compliance_analyst
    )

    # Task 2: Contextual Generation & Tailoring
    generation_task = Task(
        description=f"""
        Review the operational audit checklist produced by the auditor. Cross-reference it directly with our Company Capabilities Context dataset:
        ---
        {company_profile_text}
        ---
        Draft a formalized, enterprise-grade 3-Section RFP Proposal Response.
        
        Structure your generation EXACTLY as follows:
        # EXECUTIVE SOLUTION PROPOSAL
        
        ## SECTION 1: Tactical Architecture & Execution Strategy
        (Propose a direct technical approach addressing the client's core objectives)
        
        ## SECTION 2: Data Security & Regulatory Governance
        (Address mandatory compliance frames like SOC2, GDPR, or ISO by referencing our specific certifications)
        
        ## SECTION 3: Proven Case Performance & Uptime Assurance
        (Leverage our explicit past performance data and metrics to guarantee operational delivery)
        
        Ensure the final response text utilizes clean, highly readable Markdown formatting.
        """,
        expected_output="A comprehensive, beautifully structured corporate proposal response draft in clean Markdown.",
        agent=proposal_writer
    )

    # Sequential Assembly Line Crew Coordination
    rfp_crew = Crew(
        agents=[compliance_analyst, proposal_writer],
        tasks=[extraction_task, generation_task],
        process=Process.sequential,
        verbose=True
    )

    raw_result = rfp_crew.kickoff()
    return raw_result