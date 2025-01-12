import streamlit as st
from datetime import datetime
import pytz

def render_strategic_qa_section(supabase):
    """Render the Strategic Q&A section of My Profile."""
    st.write("### 💭 Strategic Q&A")
    
    # Get user's latest completed Q&A session
    sessions = (supabase.table("strategic_qa_sessions")
               .select("*")
               .eq("user_id", st.session_state.user.id)
               .eq("status", "complete")  # Only get completed sessions
               .order("created_at.desc")
               .execute())
    
    if sessions.data:
        latest_session = sessions.data[0]
        
        # Get responses for this session
        responses = (supabase.table("strategic_qa_responses")
                    .select("*")
                    .eq("session_id", latest_session["id"])
                    .order("question_number")
                    .execute())
        
        if responses.data:
            # Show completion status
            try:
                # Parse timestamp with timezone
                completed_date = datetime.strptime(latest_session["created_at"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
                completed_date = pytz.utc.localize(completed_date)
                st.success(f"**Completed** on {completed_date.strftime('%b %d, %Y')}", icon="✅")
            except Exception as e:
                st.success("**Completed**", icon="✅")
            
            # View responses
            with st.expander("View Strategic Q&A Responses", expanded=False):
                for response in responses.data:
                    st.write(f"#### Question {response['question_number']}")
                    st.info(response["question_text"])
                    
                    st.write("**Your Response:**")
                    st.write(response["response_text"])
                    
                    if response.get("analysis_text"):
                        st.write("**AI Analysis:**")
                        st.write(response["analysis_text"])
                    
                    st.write("---")
            
            # Option to start new session
            if st.button("Start New Q&A Session", use_container_width=True):
                st.switch_page("pages/3_Strategic_QA.py")
                
        else:
            st.info("No responses found for this session.", icon="ℹ️")
            if st.button("Start New Q&A Session", use_container_width=True):
                st.switch_page("pages/3_Strategic_QA.py")
    else:
        # Check for in-progress session
        in_progress = (supabase.table("strategic_qa_sessions")
                      .select("*")
                      .eq("user_id", st.session_state.user.id)
                      .eq("status", "in_progress")
                      .execute())
        
        if in_progress.data:
            st.info("You have an incomplete Strategic Q&A session.", icon="ℹ️")
            
            # Get responses for in-progress session
            responses = (supabase.table("strategic_qa_responses")
                        .select("*")
                        .eq("session_id", in_progress.data[0]["id"])
                        .execute())
            
            # Show progress
            completed = len([r for r in responses.data if r.get("response_text")])
            total = 3  # Total number of questions
            st.progress(completed / total, f"Completed {completed} of {total} questions")
            
            if st.button("Continue Q&A Session", use_container_width=True):
                st.switch_page("pages/3_Strategic_QA.py")
        else:
            st.info("You haven't started the Strategic Q&A yet.", icon="ℹ️")
            if st.button("Begin Strategic Q&A", use_container_width=True):
                st.switch_page("pages/3_Strategic_QA.py")
