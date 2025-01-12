import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from pages.components.auth import render_auth_ui, render_user_menu

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", "")
)

# Page config
st.set_page_config(
    page_title="Welcome - WhiteCoat",
    page_icon="👋",
    initial_sidebar_state="expanded",
    layout="centered"
)

# Render user menu in sidebar
render_user_menu(supabase)

# Main content
if not st.session_state.get("authenticated"):
    st.title("Welcome to WhiteCoat")
    st.write("Please log in or sign up to continue.")
    render_auth_ui(supabase)
else:
    # Get user's name from metadata
    user = st.session_state.user
    user_name = user.user_metadata.get("first_name", "there")

    st.title("WHITECOAT")

    st.markdown(f"""
    ### Welcome, {user_name}!

    We're excited to join you on your journey toward medical school. To start, let's make sure we understand your story and goals as clearly as possible—your unique experiences, challenges, and aspirations are the foundation for everything we'll do together.

    Here's what we'll need to get started:

    * **Your Transcript:** This helps us understand your academic progress and where you're headed.
    * **Your Resume:** This shows us your experiences so far—clinical, research, leadership, and beyond.
    * **A Few Quick Questions:** These will help us learn about your motivations, priorities, and goals so we can tailor our guidance just for you.

    This process is streamlined to guide you every step of the way. Once you're done, we'll create a **Personalized Pre-Med Profile Report** for you—a clear, concise snapshot of where you stand now and where you're headed.

    Ready to begin? Let's build your profile together!
    """)

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📄 Upload Transcript", use_container_width=True):
            st.switch_page("pages/2_Document_Upload.py")  # Updated path

    with col2:
        if st.button("📝 Upload Resume", use_container_width=True):
            st.switch_page("pages/2_Document_Upload.py")  # Updated path

    with col3:
        if st.button("❓ Begin Questionnaire", use_container_width=True):
            st.switch_page("pages/2_Questionnaire.py")

    # Progress tracker
    st.write("---")
    st.write("### Your Progress")
    
    # Check documents
    docs = supabase.table("user_documents").select("*").eq("user_id", user.id).execute()
    has_transcript = any(d["document_type"] == "transcript" for d in docs.data) if docs.data else False
    has_resume = any(d["document_type"] == "cv" for d in docs.data) if docs.data else False
    
    # Check questionnaire
    questionnaire = supabase.table("questionnaire_responses").select("*").eq("user_id", user.id).execute()
    has_questionnaire = bool(questionnaire.data)
    
    # Show status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"Transcript: {'✅' if has_transcript else '⏳'}")
    
    with col2:
        st.write(f"Resume: {'✅' if has_resume else '⏳'}")
    
    with col3:
        st.write(f"Questionnaire: {'✅' if has_questionnaire else '⏳'}")
    
    # Show next step if all complete
    if has_transcript and has_resume and has_questionnaire:
        st.success("✅ All items complete!")
        if st.button("Continue to Profile Summary"):
            st.switch_page("pages/2_Profile.py")
