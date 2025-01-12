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
    page_title="Strategic Q&A - WhiteCoat",
    page_icon="💭",
    initial_sidebar_state="expanded"
)

# Check authentication
if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access this page.")
    st.stop()

def get_approved_summary():
    """Get user's latest approved summary."""
    try:
        result = supabase.table("ai_summaries").select("*").eq("user_id", st.session_state.user.id).eq("status", "approved").order("version", desc=True).limit(1).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Error loading summary: {str(e)}")
        return None

def get_or_create_session(summary_id):
    """Get existing session or create new one."""
    try:
        # Check for existing in-progress session
        result = supabase.table("strategic_qa_sessions").select("*").eq("user_id", st.session_state.user.id).eq("status", "in_progress").execute()
        if result.data:
            return result.data[0]
        
        # Create new session
        data = {
            "user_id": st.session_state.user.id,
            "summary_id": summary_id,
            "status": "in_progress"
        }
        result = supabase.table("strategic_qa_sessions").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Error managing session: {str(e)}")
        return None

def get_session_responses(session_id):
    """Get all responses for a session."""
    try:
        result = supabase.table("strategic_qa_responses").select("*").eq("session_id", session_id).order("question_number").execute()
        return result.data
    except Exception as e:
        st.error(f"Error loading responses: {str(e)}")
        return []

def generate_question(approved_summary, question_number, previous_responses=None):
    """Generate next strategic question based on context."""
    try:
        # Format context
        context = f"""
        Approved Profile Summary:
        {approved_summary['summary']}
        """
        
        if previous_responses:
            context += f"""
            Previous Questions and Answers:
            {json.dumps(previous_responses, indent=2)}
            """
        
        # System prompts for each question
        prompts = {
            1: """You are an expert pre-med advisor conducting a strategic discussion. Based on the applicant's profile summary, generate a thoughtful first question that explores their most significant strength or unique aspect that could differentiate them in medical school applications. Focus on drawing out specific examples and details that could enrich their application narrative.""",
            2: """Based on the profile and previous discussion, generate a question that addresses their most pressing gap or area for growth. Frame it constructively, focusing on their plans and strategies for addressing this area.""",
            3: """For the final question, focus on their long-term vision and alignment with their chosen path. Help them articulate how their experiences and goals connect to their future in medicine."""
        }
        
        # Generate question
        response = openai_client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": prompts[question_number]},
                {"role": "user", "content": context}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Error generating question: {str(e)}")
        return None

def analyze_response(question, answer, approved_summary):
    """Analyze user's response and provide insights."""
    try:
        context = f"""
        Question: {question}
        User's Response: {answer}
        
        Profile Summary:
        {approved_summary['summary']}
        """
        
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
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Error analyzing response: {str(e)}")
        return None

def save_qa_response(session_id, question_number, question, response, analysis):
    """Save Q&A response to database."""
    try:
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
        st.error(f"Error saving response: {str(e)}")
        return None

def complete_session(session_id):
    """Mark session as complete."""
    try:
        data = {"status": "complete"}
        result = supabase.table("strategic_qa_sessions").update(data).eq("id", session_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Error completing session: {str(e)}")
        return None

# Main content
st.title("Strategic Q&A Discussion")

# Get approved summary
approved_summary = get_approved_summary()
if not approved_summary:
    st.error("Please complete and approve your profile summary first.")
    if st.button("Return to Summary"):
        st.switch_page("pages/2_Summary.py")
    st.stop()

# Show approved summary in expander
with st.expander("View Approved Summary"):
    st.write(approved_summary["summary"])

# Get or create session
qa_session = get_or_create_session(approved_summary["id"])
if not qa_session:
    st.error("Error managing Q&A session.")
    st.stop()

# Get existing responses
responses = get_session_responses(qa_session["id"])
current_q = len(responses) + 1

if current_q <= 3:
    st.write(f"Question {current_q} of 3")
    
    # Show previous Q&A
    for resp in responses:
        with st.expander(f"Question {resp['question_number']}", expanded=False):
            st.write("Question:", resp["question_text"])
            st.write("Your response:", resp["response_text"])
            st.write("Analysis:", resp["analysis_text"])
    
    # Generate current question if needed
    if "current_question" not in st.session_state:
        question = generate_question(approved_summary, current_q, responses)
        if question:
            st.session_state.current_question = question
    
    # Display current question
    st.write(st.session_state.current_question)
    
    # Handle response
    response = st.text_area("Your response:")
    if st.button("Submit Response"):
        if response:
            # Generate analysis
            analysis = analyze_response(
                st.session_state.current_question,
                response,
                approved_summary
            )
            
            if analysis:
                # Save response
                if save_qa_response(
                    qa_session["id"],
                    current_q,
                    st.session_state.current_question,
                    response,
                    analysis
                ):
                    # Show analysis
                    st.write("Analysis:", analysis)
                    
                    # Clear current question
                    if "current_question" in st.session_state:
                        del st.session_state.current_question
                    
                    # Show next step
                    if current_q < 3:
                        if st.button("Continue to Next Question"):
                            st.rerun()
                    else:
                        if st.button("Complete Discussion"):
                            if complete_session(qa_session["id"]):
                                st.success("✅ Strategic Discussion Complete")
                                st.rerun()

else:
    # Show completion state
    st.success("✅ Strategic Discussion Complete")
    
    # Show all Q&A
    for resp in responses:
        with st.expander(f"Question {resp['question_number']}", expanded=True):
            st.write("Question:", resp["question_text"])
            st.write("Your response:", resp["response_text"])
            st.write("Analysis:", resp["analysis_text"])
    
    # Option to generate report
    if st.button("Generate Final Report"):
        st.switch_page("pages/4_Report.py")
