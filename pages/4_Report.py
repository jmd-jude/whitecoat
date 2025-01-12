import os
import json
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", "")
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o")

# Page config
st.set_page_config(
    page_title="PreMed Profile Report - WhiteCoat",
    page_icon="📋",
    initial_sidebar_state="expanded",
    layout="wide"
)

# Check authentication
if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access this page.")
    st.stop()

def check_prerequisites():
    """Check if all required artifacts are ready."""
    try:
        # Check documents
        docs = supabase.table("user_documents").select("*").eq("user_id", st.session_state.user.id).execute()
        has_cv = any(d["document_type"] == "cv" for d in docs.data)
        has_transcript = any(d["document_type"] == "transcript" for d in docs.data)
        
        # Check questionnaire
        questionnaire = supabase.table("questionnaire_responses").select("*").eq("user_id", st.session_state.user.id).execute()
        
        # Check approved summary
        summary = supabase.table("ai_summaries").select("*").eq("user_id", st.session_state.user.id).eq("status", "approved").execute()
        
        # Check completed Q&A
        qa_session = supabase.table("strategic_qa_sessions").select("*").eq("user_id", st.session_state.user.id).eq("status", "complete").execute()
        
        return {
            "documents": {
                "ready": has_cv and has_transcript,
                "cv": has_cv,
                "transcript": has_transcript
            },
            "questionnaire": bool(questionnaire.data),
            "summary": bool(summary.data),
            "qa_session": bool(qa_session.data)
        }
    except Exception as e:
        st.error(f"Error checking prerequisites: {str(e)}")
        return None

def load_artifacts():
    """Load all artifacts needed for report generation."""
    try:
        # Load documents
        documents = supabase.table("user_documents").select("*").eq("user_id", st.session_state.user.id).execute()
        
        # Load questionnaire
        questionnaire = supabase.table("questionnaire_responses").select("*").eq("user_id", st.session_state.user.id).execute()
        
        # Load approved summary
        summary = supabase.table("ai_summaries").select("*").eq("user_id", st.session_state.user.id).eq("status", "approved").order("version", desc=True).limit(1).execute()
        
        # Load Q&A session
        qa_session = supabase.table("strategic_qa_sessions").select("*").eq("user_id", st.session_state.user.id).eq("status", "complete").order("created_at", desc=True).limit(1).execute()
        if qa_session.data:
            qa_responses = supabase.table("strategic_qa_responses").select("*").eq("session_id", qa_session.data[0]["id"]).order("question_number").execute()
        else:
            qa_responses = None
        
        return {
            "documents": documents.data,
            "questionnaire": questionnaire.data[0] if questionnaire.data else None,
            "summary": summary.data[0] if summary.data else None,
            "qa_session": {
                "session": qa_session.data[0] if qa_session.data else None,
                "responses": qa_responses.data if qa_responses else None
            }
        }
    except Exception as e:
        st.error(f"Error loading artifacts: {str(e)}")
        return None

def get_active_template():
    """Get the active report template."""
    try:
        result = supabase.table("report_templates").select("*").eq("is_active", True).order("version", desc=True).limit(1).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Error loading template: {str(e)}")
        return None

def generate_section(template_section, artifacts):
    """Generate content for a report section."""
    try:
        # Format context from artifacts
        context = f"""
        Documents:
        {json.dumps(artifacts['documents'], indent=2)}
        
        Questionnaire Responses:
        {json.dumps(artifacts['questionnaire'], indent=2)}
        
        Approved Summary:
        {json.dumps(artifacts['summary'], indent=2)}
        
        Q&A Session:
        {json.dumps(artifacts['qa_session'], indent=2)}
        """
        
        # Generate section content
        response = openai_client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": template_section["prompt"]},
                {"role": "user", "content": context}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating section: {str(e)}")
        return None

def save_report(template, content, artifacts):
    """Save generated report."""
    try:
        # Format artifacts reference
        artifacts_ref = {
            "documents": {
                doc["document_type"]: {
                    "id": doc["id"],
                    "version": doc["created_at"]
                } for doc in artifacts["documents"]
            },
            "questionnaire": {
                "id": artifacts["questionnaire"]["id"],
                "version": artifacts["questionnaire"]["created_at"]
            },
            "summary": {
                "id": artifacts["summary"]["id"],
                "version": artifacts["summary"]["version"]
            },
            "qa_session": {
                "id": artifacts["qa_session"]["session"]["id"],
                "completed_at": artifacts["qa_session"]["session"]["updated_at"]
            }
        }
        
        data = {
            "user_id": st.session_state.user.id,
            "template_id": template["id"],
            "template_version": template["version"],
            "status": "draft",
            "content": content,
            "artifacts": artifacts_ref
        }
        
        result = supabase.table("reports").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Error saving report: {str(e)}")
        return None

def get_latest_report():
    """Get user's latest report."""
    try:
        result = supabase.table("reports").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).limit(1).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Error loading report: {str(e)}")
        return None

def finalize_report(report_id):
    """Mark report as final."""
    try:
        # Use target_id to match SQL function parameter
        result = supabase.rpc("finalize_report", {"target_id": report_id}).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Error finalizing report: {str(e)}")
        return None

# Main content
st.title("PreMed Profile Report")

# Get latest report
report = get_latest_report()

if report and report["status"] == "draft":
    st.info("📝 Draft Report")
    
    # Show report preview
    st.write("### Report Preview")
    for section in report["content"]["sections"]:
        with st.expander(section["name"], expanded=True):
            st.write(section["content"])
    
    # Finalize option
    st.write("### Finalize Report")
    st.write("Review the report above and click below to finalize it.")
    if st.button("✅ Finalize Report"):
        if finalize_report(report["id"]):
            st.success("Report finalized!")
            st.rerun()
    
    # Regenerate option
    if st.button("🔄 Regenerate Report"):
        # Clear report from session state
        if "current_report" in st.session_state:
            del st.session_state.current_report
        st.rerun()

elif report and report["status"] == "final":
    st.success("✅ Final Report")
    
    # Show report sections
    for section in report["content"]["sections"]:
        with st.expander(section["name"], expanded=True):
            st.write(section["content"])
    
    # Option to generate new report
    if st.button("Generate New Report"):
        # Clear report from session state
        if "current_report" in st.session_state:
            del st.session_state.current_report
        st.rerun()

else:
    # Check prerequisites
    prereqs = check_prerequisites()
    if not prereqs:
        st.error("Error checking prerequisites.")
        st.stop()

    # Show prerequisite status
    st.write("### Prerequisites")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Documents:")
        st.write(f"- CV: {'✅' if prereqs['documents']['cv'] else '❌'}")
        st.write(f"- Transcript: {'✅' if prereqs['documents']['transcript'] else '❌'}")
        st.write(f"- Questionnaire: {'✅' if prereqs['questionnaire'] else '❌'}")
    with col2:
        st.write("Profile Summary:")
        st.write(f"- Approved Summary: {'✅' if prereqs['summary'] else '❌'}")
        st.write(f"- Q&A Complete: {'✅' if prereqs['qa_session'] else '❌'}")

    # Check if ready to proceed
    all_ready = all([
        prereqs['documents']['ready'],
        prereqs['questionnaire'],
        prereqs['summary'],
        prereqs['qa_session']
    ])

    if not all_ready:
        st.error("Please complete all prerequisites before generating your report.")
        st.stop()

    # Load template
    template = get_active_template()
    if not template:
        st.error("No active report template found.")
        st.stop()

    # Show generation options
    st.write("### Report Generation")
    st.write("Ready to generate your PreMed Profile Report!")

    if st.button("Generate Report"):
        with st.spinner("Loading artifacts..."):
            artifacts = load_artifacts()
            if not artifacts:
                st.error("Error loading artifacts.")
                st.stop()
        
        # Generate each section
        sections = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, section in enumerate(template["sections"]["sections"]):
            status_text.write(f"Generating {section['name']}...")
            content = generate_section(section, artifacts)
            if content:
                sections.append({
                    "name": section["name"],
                    "content": content
                })
            progress_bar.progress((i + 1) / len(template["sections"]["sections"]))
        
        if len(sections) == len(template["sections"]["sections"]):
            # Save report
            report = save_report(template, {"sections": sections}, artifacts)
            if report:
                st.success("Report generated successfully!")
                st.session_state.current_report = report
                st.rerun()
            else:
                st.error("Error saving report.")
