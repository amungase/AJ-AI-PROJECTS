import os
from crewai import Agent, Task, Crew, Process, LLM

def run_rfp_pipeline(company_profile_text, rfp_requirements_text):
    
    # FIX: Configured to use the active 'gemini/gemini-2.5-flash' model
    # wrapped cleanly inside the CrewAI LLM class exactly like pipeline.py
    gemini_llm = LLM(
        model="gemini/gemini-2.5-flash",
        api_key=os.environ.get("GOOGLE_API_KEY")
    )

    # ---------------------------------------------------------
    # 1. AGENT DEFINITIONS (The Specialized Team)
    # ---------------------------------------------------------
    
    # Agent 1: The Requirement Extraction Analyst
    compliance_analyst = Agent(
        role="Senior Compliance and Extraction Specialist",
        goal="Identify and index every explicit requirement and compliance flag inside an RFP document.",
        backstory="An expert auditor with an eye for legal and technical fine print. You extract raw needs perfectly.",
        verbose=True,
        allow_delegation=False,
        llm=gemini_llm
    )

    # Agent 2: The Tactical Proposal Writer
    proposal_writer = Agent(
        role="Principal Executive Proposal Copywriter",
        goal="Draft data-driven, structured corporate responses matching company credentials against client criteria.",
        backstory="A high-impact writer who knows how to format professional proposals, frame capabilities positively, and retain strict truthfulness.",
        verbose=True,
        allow_delegation=False,
        llm=gemini_llm
    )

    # ---------------------------------------------------------
    # 2. TASK DEFINITIONS (The Assembly Line)
    # ---------------------------------------------------------

    # Task 1: Extraction Challenge
    extraction_task = Task(
        description=f"""
        Analyze the client's RFP context document carefully:
        ---
        {rfp_requirements_text}
        ---
        Extract a comprehensive bulleted list of all technical demands, security compliance mandates, and core objectives.
        """,
        expected_output="A structured list summarizing mandatory compliance points and project performance demands.",
        agent=compliance_analyst
    )

    # Task 2: Writing & Integration Challenge
    generation_task = Task(
        description=f"""
        Using the extracted evaluation parameters from the analyst, leverage our official Company Capabilities Context:
        ---
        {company_profile_text}
        ---
        Draft a formalized, highly tailored 3-Section RFP Proposal Response.
        Include:
        Section 1: Executive Approach (Addressing Project Objectives)
        Section 2: Technical Execution & Security Compliance (Direct responses to compliance frameworks)
        Section 3: Proof of Capability (Leveraging Past Performance Data)
        
        Keep the layout professional, polished, and structured in clean Markdown format.
        """,
        expected_output="The final beautifully written corporate proposal response document in Markdown format.",
        agent=proposal_writer
    )

    # ---------------------------------------------------------
    # 3. KICKOFF CREW PROCESS
    # ---------------------------------------------------------
    rfp_crew = Crew(
        agents=[compliance_analyst, proposal_writer],
        tasks=[extraction_task, generation_task],
        process=Process.sequential, 
        verbose=True
    )

    # Kick off execution and obtain the raw output text
    raw_result = rfp_crew.kickoff()
    return raw_result