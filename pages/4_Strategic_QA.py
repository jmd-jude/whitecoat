import os
import json
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables and initialize clients
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
AI_MODEL = os.getenv("AI_MODEL", "gpt-4")

# Page configuration
st.set_page_config(
    page_title="Strategic Q&A - WhiteCoat",
    page_icon="💭",
    initial_sidebar_state="expanded"
)

# Initialize session states
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'qa_session' not in st.session_state:
    st.session_state.qa_session = None
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'debug_logs' not in st.session_state:
    st.session_state.debug_logs = []
if 'needs_question' not in st.session_state:
    st.session_state.needs_question = False

# Authentication check
if not st.session_state.authenticated:
    st.warning("Please log in to access this page.")
    st.stop()

def log_debug(message):
    """Add a debug message to session state logs."""
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
    st.session_state.debug_logs.append(message)

def get_approved_summary():
    """Get user's latest approved summary."""
    try:
        log_debug("Fetching approved summary")
        result = supabase.table("ai_summaries") \
            .select("*") \
            .eq("user_id", st.session_state.user.id) \
            .eq("status", "approved") \
            .order("version", desc=True) \
            .limit(1) \
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        error_msg = f"Error loading summary: {str(e)}"
        log_debug(error_msg)
        st.error(error_msg)
        return None

def get_session_responses(session_id):
    """Get all responses for current session."""
    try:
        log_debug(f"Fetching responses for session {session_id}")
        result = supabase.table("strategic_qa_responses") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("question_number") \
            .execute()
        return result.data
    except Exception as e:
        error_msg = f"Error loading responses: {str(e)}"
        log_debug(error_msg)
        st.error(error_msg)
        return []

def generate_question(approved_summary, question_number, previous_responses=None):
    """Generate the next question based on context."""
    try:
        log_debug(f"Generating question {question_number}")
        
        # Get document analysis
        analyses = supabase.table("document_analysis") \
            .select("document_type, parsed_data") \
            .eq("user_id", st.session_state.user.id) \
            .eq("status", "complete") \
            .execute()
        
        log_debug(f"Got {len(analyses.data)} document analyses")
        
        context = {
            "summary": approved_summary['summary'],
            "parsed_documents": analyses.data,
            "previous_responses": previous_responses or []
        }
        
        prompts = {
            1: """You are an expert pre-med advisor conducting a strategic discussion. Based on the applicant's profile summary, generate a thoughtful first question that explores their most significant strength or unique aspect that could differentiate them in medical school applications. Focus on drawing out specific examples and details that could enrich their application narrative.""",
            2: """Based on the profile and previous discussion, generate a question that addresses their most pressing gap or area for growth. Frame it constructively, focusing on their plans and strategies for addressing this area.""",
            3: """For the final question, focus on their long-term vision and alignment with their chosen path. Help them articulate how their experiences and goals connect to their future in medicine."""
        }
        
        context_str = f"""
        Approved Profile Summary:
        {context['summary']}
        
        Analyzed Documents:
        {json.dumps(context['parsed_documents'], indent=2)}
        
        Previous Questions and Answers:
        {json.dumps(context['previous_responses'], indent=2)}
        """
        
        log_debug("Calling OpenAI API")
        
        response = openai_client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": prompts[question_number]},
                {"role": "user", "content": context_str}
            ],
            temperature=0.7
        )
        
        log_debug("OpenAI API call completed")
        return response.choices[0].message.content
    except Exception as e:
        error_msg = f"Error generating question: {type(e).__name__}: {str(e)}"
        log_debug(error_msg)
        st.error(error_msg)
        return None

def save_qa_response(session_id, question_number, question, response, analysis):
    """Save Q&A response to database."""
    try:
        log_debug(f"Saving response for question {question_number}")
        data = {
            "session_id": session_id,
            "question_number": question_number,
            "question_text": question,
            "response_text": response,
            "analysis_text": analysis
        }
        result = supabase.table("strategic_qa_responses").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        error_msg = f"Error saving response: {str(e)}"
        log_debug(error_msg)
        st.error(error_msg)
        return None

def handle_session_start(approved_summary):
    """Start a new Q&A session."""
    try:
        log_debug("Starting new session")
        data = {
            "user_id": st.session_state.user.id,
            "summary_id": approved_summary["id"],
            "status": "in_progress"
        }
        log_debug(f"Session data: {data}")
        
        result = supabase.table("strategic_qa_sessions").insert(data).execute()
        log_debug(f"Session creation result: {result.data}")
        
        if result.data:
            st.session_state.qa_session = result.data[0]
            st.session_state.needs_question = True
            log_debug("Session created and stored in state")
            return True
        else:
            st.error("No data returned from session creation")
            return False
    except Exception as e:
        error_msg = f"Error starting session: {type(e).__name__}: {str(e)}"
        log_debug(error_msg)
        st.error(error_msg)
        return False

def analyze_response(question, answer, approved_summary):
    """Analyze user's response and provide insights."""
    try:
        log_debug("Analyzing response")
        analyses = supabase.table("document_analysis") \
            .select("document_type, parsed_data") \
            .eq("user_id", st.session_state.user.id) \
            .eq("status", "complete") \
            .execute()
            
        context = f"""
        Question: {question}
        User's Response: {answer}
        
        Profile Summary:
        {approved_summary['summary']}
        
        Analyzed Documents:
        {json.dumps(analyses.data, indent=2)}
        """
        
        log_debug("Calling OpenAI for analysis")
        response = openai_client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": """You are an expert pre-med advisor. Analyze the applicant's response and provide:
                1. Key insights from their answer
                2. Specific strengths demonstrated
                3. Areas that could be developed further
                4. How this connects to their overall application narrative
                
                Be constructive and specific in your analysis."""},
                {"role": "user", "content": context}
            ],
            temperature=0.7
        )
        log_debug("Analysis completed")
        return response.choices[0].message.content
    except Exception as e:
        error_msg = f"Error analyzing response: {str(e)}"
        log_debug(error_msg)
        st.error(error_msg)
        return None

# Main page content
st.title("Strategic Q&A Discussion")

# Get approved summary
approved_summary = get_approved_summary()
if not approved_summary:
    st.error("Please complete and approve your profile summary first.")
    st.stop()

with st.expander("View Approved Summary"):
    st.write(approved_summary["summary"])

# Main Q&A flow
if not st.session_state.qa_session:
    st.write("Ready to begin your Strategic Q&A Discussion.")
    if st.button("Start Q&A Discussion", use_container_width=True):
        if handle_session_start(approved_summary):
            st.rerun()
else:
    responses = get_session_responses(st.session_state.qa_session["id"])
    current_q = len(responses) + 1
    
    if current_q <= 3:
        st.write(f"Question {current_q} of 3")
        
        # Show previous responses
        for resp in responses:
            with st.expander(f"Question {resp['question_number']}", expanded=False):
                st.write("Question:", resp["question_text"])
                st.write("Your response:", resp["response_text"])
                st.write("Analysis:", resp["analysis_text"])
        
        # Generate and display current question
        if st.session_state.needs_question:
            st.session_state.current_question = generate_question(
                approved_summary, current_q, responses
            )
            st.session_state.needs_question = False
            st.rerun()
        
        if st.session_state.current_question:
            st.write(st.session_state.current_question)
            response = st.text_area("Your response:")
            
            if st.button("Submit Response"):
                if response:
                    analysis = analyze_response(
                        st.session_state.current_question,
                        response,
                        approved_summary
                    )
                    
                    if analysis and save_qa_response(
                        st.session_state.qa_session["id"],
                        current_q,
                        st.session_state.current_question,
                        response,
                        analysis
                    ):
                        st.write("Analysis:", analysis)
                        st.session_state.needs_question = True
                        st.session_state.current_question = None
                        st.rerun()
    
    # After all questions are answered, show completion button
    responses = get_session_responses(st.session_state.qa_session["id"])
    if len(responses) == 3 and st.session_state.qa_session["status"] == "in_progress":
        st.info("All questions completed. Click below to finish the discussion.")
        if st.button("Complete Discussion"):
            log_debug(f"Attempting to complete session {st.session_state.qa_session['id']}")
            try:
                result = supabase.table("strategic_qa_sessions") \
                    .update({"status": "complete"}) \
                    .eq("id", st.session_state.qa_session["id"]) \
                    .execute()
                log_debug(f"Update result: {result.data}")
                
                if result.data:
                    # Instead of clearing session, just update its status
                    st.session_state.qa_session["status"] = "complete"
                    st.success("✅ Strategic Discussion Complete!")
                    st.rerun()
                else:
                    st.error("Failed to update session status")
            except Exception as e:
                log_debug(f"Error completing session: {str(e)}")
                st.error(f"Error completing session: {str(e)}")
    
    # Show final state for completed sessions
    if st.session_state.qa_session and st.session_state.qa_session["status"] == "complete":
        st.success("✅ Strategic Discussion Complete!")
        for resp in responses:
            with st.expander(f"Question {resp['question_number']}", expanded=True):
                st.write("Question:", resp["question_text"])
                st.write("Your response:", resp["response_text"])
                st.write("Analysis:", resp["analysis_text"])