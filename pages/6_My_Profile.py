import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from pages.components.documents import render_documents_section
from pages.components.questionnaire import render_questionnaire_section
from pages.components.strategic_qa import render_strategic_qa_section

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", "")
)

# Page config
st.set_page_config(
    page_title="My Profile - WhiteCoat",
    page_icon="📂",
    layout="wide"
)

# Check authentication
if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access this page.")
    st.stop()

# Header
st.title("My Profile")
st.write("View and manage your profile information")

# Status Overview
col1, col2, col3 = st.columns(3)

with col1:
    # Get document status
    docs = supabase.table("user_documents").select("*").eq("user_id", st.session_state.user.id).execute()
    has_cv = any(d["document_type"] == "cv" for d in docs.data) if docs.data else False
    has_transcript = any(d["document_type"] == "transcript" for d in docs.data) if docs.data else False
    
    if has_cv and has_transcript:
        st.success("Documents: Complete", icon="✅")
    else:
        st.warning("Documents: Incomplete", icon="⚠️")

with col2:
    # Get questionnaire status
    questionnaire = supabase.table("questionnaire_responses").select("*").eq("user_id", st.session_state.user.id).execute()
    if questionnaire.data:
        st.success("Questionnaire: Complete", icon="✅")
    else:
        st.warning("Questionnaire: Incomplete", icon="⚠️")

with col3:
    # Get Q&A status
    qa_sessions = (supabase.table("strategic_qa_sessions")
                  .select("*")
                  .eq("user_id", st.session_state.user.id)
                  .eq("status", "complete")
                  .execute())
    if qa_sessions.data:
        st.success("Strategic Q&A: Complete", icon="✅")
    else:
        st.warning("Strategic Q&A: Incomplete", icon="⚠️")

st.write("---")

# Documents Section
render_documents_section(supabase)

st.write("---")

# Questionnaire Section
render_questionnaire_section(supabase)

st.write("---")

# Initial Profile Summary Section
st.write("### 📈 Initial Profile Summary")

# Check if initial prerequisites are complete
initial_complete = (has_cv and has_transcript) and bool(questionnaire.data)

if initial_complete:
    st.success("""
    Initial profile sections complete! You can now get an initial assessment based on:
    - Document analysis
    - Questionnaire responses
    
    This will help guide your Strategic Q&A discussion.
    """, icon="✅")
    
    if st.button("View Initial Profile Summary", use_container_width=True):
        st.switch_page("pages/3_Profile.py")
else:
    st.info("""
    Your initial profile summary will be available after:
    - Uploading your CV and transcript
    - Completing the questionnaire
    """, icon="ℹ️")

st.write("---")

# Strategic Q&A Section
render_strategic_qa_section(supabase)

st.write("---")

# Final PreMed Report Section
st.write("### 📊 PreMed Report")

# Check if all prerequisites are complete
all_complete = initial_complete and bool(qa_sessions.data)

if all_complete:
    st.success("""
    All sections complete! Your comprehensive PreMed Report includes:
    - Document analysis
    - Questionnaire insights
    - Strategic Q&A discussion
    - Personalized recommendations
    
    This report provides a complete assessment of your medical school application readiness.
    """, icon="✅")
    
    if st.button("View PreMed Report", use_container_width=True):
        st.switch_page("pages/5_Report.py")
else:
    st.info("""
    Your final PreMed Report will be available after completing:
    - Initial profile sections (Documents & Questionnaire)
    - Strategic Q&A discussion
    """, icon="ℹ️")
