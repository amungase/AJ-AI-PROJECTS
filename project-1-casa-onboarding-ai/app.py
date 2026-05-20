import os
import sys
import streamlit as st

# Force Python to recognize your current project folder path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.database import OnboardingVectorStore
from components.pipeline import CASAOnboardingEngine

st.set_page_config(page_title="CASA AI Core Compliance Panel", layout="wide")

st.title("🏦 CASA Corporate Onboarding Modernization Matrix")
st.caption("Enterprise Reference Build — Agentic AI Verification & Compliance Pipeline with HITL Breakpoints")

# Side Navigation Controls
with st.sidebar:
    st.header("Admin Control Board")
    if st.button("Seed Regulatory Vector DB (Pinecone)"):
        with st.spinner("Syncing compliance registries into vector cells..."):
            try:
                store = OnboardingVectorStore()
                store.seed_regulatory_knowledge("data/regulatory_kb.txt")
                st.success("Vector DB synchronization complete. Storage Active.")
            except Exception as e:
                st.error(f"Seeding Failed. Verify keys or Index setup. Error: {e}")

# Split Workspace layout
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Inbound Corporate Application Records")
    
    sample_doc = st.text_area(
        label="Extracted Document Text Array (Simulated OCR Payload)",
        height=250,
        value="""COMPANY DOC: Phoenix Apex Trade Solutions LLC
REGISTRATION ID: CORP-992811-Z
DOCUMENT TYPE: Corporate Partnership Certificate
OPERATIONAL NOTE: Entity is established to run cross-border distribution lines. 
OWNERSHIP RUN-DOWN: Chief Executive Officer Marcus Vance holds 80% total corporate voting stocks. 
SIGNATORY NOTE: Missing standard Annex-B signatures for secondary treasury execution nodes."""
    )
    
    st.markdown("### 🛑 Human-in-the-Loop Override Interface")
    human_notes = st.text_input(
        label="Auditor Overrides / Context Updates (Supplied back to Agent Memory dynamically)",
        placeholder="e.g., 'Marcus Vance verified passport identity via face-match step'"
    )
    
    trigger_pipeline = st.button("Execute Multi-Agent Onboarding Verification Flow", type="primary")

with col_right:
    st.subheader("AI Compliance Automation Insights & Payload Output")
    
    if trigger_pipeline:
        with st.spinner("Executing secure pipeline execution arrays..."):
            try:
                engine = CASAOnboardingEngine()
                payload = engine.run_onboarding_pipeline(sample_doc, human_override_notes=human_notes)
                
                if payload.get("verification_status") == "APPROVED":
                    st.success("🎉 CORE SYSTEM TRANSACTION DISPATCH READY: APPLICATION COMPLIANT")
                else:
                    st.error("🚨 VERIFICATION HOLD GENERATED: MANUAL REMEDIATION REQUIRED")
                
                st.markdown(f"**Target Entity Analyzed:** `{payload.get('entity_name')}`")
                
                st.markdown("#### Detected Compliance Gaps")
                gaps = payload.get("compliance_gaps", [])
                if gaps:
                    for gap in gaps:
                        st.markdown(f"* ❌ {gap}")
                else:
                    st.markdown("* ✅ Zero structural policy gaps identified in validation block.")
                    
                st.markdown("#### Regulatory Matrix Snippet Context Applied")
                st.info(payload.get("regulatory_reference_applied", "No specific clause reference verified."))
                
                st.markdown("#### Generated System Output Structure (JSON)")
                st.json(payload)
                
            except Exception as e:
                st.error(f"Pipeline execution halted. Error details: {e}")