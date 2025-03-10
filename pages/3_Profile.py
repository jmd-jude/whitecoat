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
AI_MODEL_4o_mini = os.getenv("AI_MODEL_4o_mini", "gpt-4o")

# Page config
st.set_page_config(
    page_title="Profile - WhiteCoat",
    page_icon="📝",
    initial_sidebar_state="expanded"
)

# Check authentication
if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access this page.")
    st.stop()

def load_user_data():
    """Load user's parsed document data and questionnaire responses."""
    try:
        # Load parsed document analysis
        analyses = supabase.table("document_analysis") \
            .select("document_type, parsed_data") \
            .eq("user_id", st.session_state.user.id) \
            .eq("status", "complete") \
            .execute()
        
        # Load questionnaire responses
        responses = supabase.table("questionnaire_responses") \
            .select("responses") \
            .eq("user_id", st.session_state.user.id) \
            .execute()
        
        if not analyses.data:
            st.error("Please upload and complete document analysis first.")
            st.stop()
            
        if not responses.data:
            st.error("Please complete the questionnaire first.")
            st.stop()
            
        # Format data for GPT
        documents = {
            analysis["document_type"]: analysis["parsed_data"]
            for analysis in analyses.data
        }
            
        return documents, responses.data[0]["responses"]
    except Exception as e:
        st.error(f"Error loading user data: {str(e)}")
        st.stop()

def get_latest_summary():
    """Get user's latest summary version."""
    try:
        result = supabase.table("ai_summaries").select("*").eq("user_id", st.session_state.user.id).order("version", desc=True).limit(1).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Error loading summary: {str(e)}")
        return None

def get_summary_history():
    """Get all versions of user's summaries."""
    try:
        result = supabase.table("ai_summaries").select("*").eq("user_id", st.session_state.user.id).order("version").execute()
        return result.data
    except Exception as e:
        st.error(f"Error loading summary history: {str(e)}")
        return []

def generate_initial_summary(documents, questionnaire_responses):
    """Generate initial summary using OpenAI."""
    try:
        # Format the context for OpenAI
        context = {
            "documents": documents,  # Now using pre-parsed structured data
            "questionnaire": questionnaire_responses
        }
        
        # Generate summary using OpenAI
        response = openai_client.chat.completions.create(
            model=AI_MODEL_4o_mini,
            messages=[
                {"role": "system", "content": """You are an expert pre-med advisor. Generate a concise summary of the applicant's profile based on their documents and questionnaire responses. Focus on:
                1. Academic background and achievements
                2. Research experience and impact
                3. Clinical exposure and future plans
                4. Key priorities and goals
                
                The documents are provided in a structured format with:
                - CV data (education, research, clinical, leadership)
                - Transcript data (courses, grades, GPA)
                - Questionnaire responses
                
                Use this structured data to create a more accurate and detailed summary."""},
                {"role": "user", "content": json.dumps(context, indent=2)}
            ],
            temperature=0.2
        )
        
        summary = response.choices[0].message.content
        
        # Save to database
        data = {
            "user_id": st.session_state.user.id,
            "summary": summary,
            "status": "draft",
            "version": 1,
            "chat_history": []
        }
        
        result = supabase.table("ai_summaries").insert(data).execute()
        return result.data[0] if result.data else None
        
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

def save_revision(current_summary, revised_text, chat_history):
    """Save a new revision of the summary."""
    try:
        data = {
            "user_id": st.session_state.user.id,
            "summary": revised_text,
            "status": "draft",
            "version": current_summary["version"] + 1,
            "parent_id": current_summary["id"],
            "chat_history": chat_history
        }
        
        result = supabase.table("ai_summaries").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Error saving revision: {str(e)}")
        return None

def approve_summary(summary_id):
    """Mark a summary as approved."""
    try:
        data = {"status": "approved"}
        result = supabase.table("ai_summaries").update(data).eq("id", summary_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Error approving summary: {str(e)}")
        return None

def handle_revision_chat(current_summary):
    """Handle the revision chat interface."""
    st.write("---")
    st.write("### Revision Request")
    st.write("What would you like to clarify or revise in your profile summary?")
    
    # Show chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Enter your feedback or revision request..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Load current data for context
        documents, responses = load_user_data()
        
        # Prepare context
        context = {
            "current_summary": current_summary["summary"],
            "user_feedback": prompt,
            "documents": documents,
            "questionnaire": responses
        }
        
        # Get AI response
        response = openai_client.chat.completions.create(
            model=AI_MODEL_4o_mini,
            messages=[
                {"role": "system", "content": "You are an expert pre-med advisor helping to revise a profile summary. Use the structured document data and questionnaire responses to provide accurate revisions."},
                {"role": "user", "content": json.dumps(context, indent=2)}
            ],
            temperature=0.2
        )
        
        # Add AI response
        ai_response = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        # Generate revised summary
        revised_summary = openai_client.chat.completions.create(
            model=AI_MODEL_4o_mini,
            messages=[
                {"role": "system", "content": "Based on the conversation and structured data, generate an updated version of the summary incorporating the user's feedback."},
                {"role": "user", "content": json.dumps(context, indent=2)}
            ],
            temperature=0.2
        )
        
        # Save and refresh
        if save_revision(current_summary, revised_summary.choices[0].message.content, st.session_state.messages):
            st.rerun()

# Initialize session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main content
st.title("Your Pre-Med Profile")

# Get current summary
current_summary = get_latest_summary()

if current_summary:
    # Show version info
    st.write(f"Version: {current_summary['version']} ({current_summary['status'].title()})")
    
    # Show history button
    if st.button("View History"):
        history = get_summary_history()
        st.write("Summary History:")
        for version in history:
            with st.expander(f"Version {version['version']} - {version['status'].title()}"):
                st.write(version['summary'])
                st.write(f"Created: {version['created_at']}")
    
    # Show current summary in a container
    with st.container():
        st.write("### Your Profile Summary")
        st.write(current_summary["summary"])
        
        if current_summary["status"] == "draft":
            # Add spacing
            st.write("")
            
            # Action buttons in centered columns
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                accept_col, revise_col = st.columns(2)
                with accept_col:
                    if st.button("✅ Accept", use_container_width=True):
                        if approve_summary(current_summary["id"]):
                            st.success("Summary approved!")
                            st.rerun()
                
                with revise_col:
                    if st.button("✏️ Revise", use_container_width=True):
                        st.session_state.revising = True
            
            # Show revision interface if requested
            if st.session_state.get("revising", False):
                handle_revision_chat(current_summary)
        
        else:
            st.success("✅ Summary Approved")
            if st.button("Proceed to Q&A"):
                st.switch_page("pages/4_Strategic_QA.py")

else:
    # No summary exists yet
    st.write("No summary generated yet.")
    
    if st.button("Generate Summary"):
        with st.spinner("Generating your summary..."):
            documents, responses = load_user_data()
            if generate_initial_summary(documents, responses):
                st.success("Summary generated! Please review it above.")
                st.rerun()
