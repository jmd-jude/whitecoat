import streamlit as st
from datetime import datetime
import pytz
import json

def format_key(key):
    """Convert snake_case to Title Case and clean up key names."""
    return key.replace('_', ' ').title()

def format_value(value):
    """Format value for display."""
    if isinstance(value, (dict, list)):
        if isinstance(value, dict):
            return "\n".join(f"- {k}: {v}" for k, v in value.items())
        if not value:  # Empty list
            return "None"
        return "\n".join(f"- {v}" for v in value)
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if value is None:
        return "Not specified"
    return str(value)

def render_response_section(title, icon, keys, responses_dict):
    """Render a section of responses with an expander."""
    with st.expander(f"{icon} {title}", expanded=False):
        for key in keys:
            if key in responses_dict:
                st.write(f"**{format_key(key)}**")
                st.write(format_value(responses_dict[key]))
                st.write("")

def render_questionnaire_section(supabase):
    """Render the questionnaire section of My Profile."""
    st.write("### ❓ Questionnaire")
    
    # Get user's questionnaire responses
    responses = supabase.table("questionnaire_responses").select("*").eq("user_id", st.session_state.user.id).execute()
    
    if responses.data:
        # Show completion status
        try:
            # Parse timestamp with timezone
            completed_date = datetime.strptime(responses.data[0]["created_at"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
            completed_date = pytz.utc.localize(completed_date)
            st.success(f"**Completed** on {completed_date.strftime('%b %d, %Y')}", icon="✅")
        except Exception as e:
            st.success("**Completed**", icon="✅")
        
        # Get responses from the JSON field
        responses_dict = responses.data[0].get("responses", {})
        
        # Academic Background
        render_response_section(
            "Academic Background",
            "📚",
            ["academic_preparedness", "academic_strengths", "academic_areas", "gpa_confidence"],
            responses_dict
        )
        
        # Research Experience
        render_response_section(
            "Research Experience",
            "🔬",
            ["research_hours", "research_tasks", "research_outputs", "weekly_research_hours"],
            responses_dict
        )
        
        # Clinical & Service
        render_response_section(
            "Clinical & Service Experience",
            "👥",
            ["service_scale", "service_outcomes", "patient_interaction", "weekly_clinical_hours", 
             "clinical_certification", "weekly_volunteer_hours", "high_school_clinical_hours", 
             "post_high_school_clinical_hours"],
            responses_dict
        )
        
        # Leadership & Activities
        render_response_section(
            "Leadership & Activities",
            "👥",
            ["leadership_roles", "led_projects"],
            responses_dict
        )
        
        # Application Planning
        render_response_section(
            "Application Planning",
            "📋",
            ["application_timing", "application_gaps", "mcat_confidence", "future_contribution", 
             "greatest_weakness", "primary_focus"],
            responses_dict
        )
        
        # Update button
        if st.button("Update Responses", use_container_width=True):
            st.switch_page("pages/2_Questionnaire.py")
            
    else:
        st.info("You haven't completed the questionnaire yet.", icon="ℹ️")
        if st.button("Begin Questionnaire", use_container_width=True):
            st.switch_page("pages/2_Questionnaire.py")
