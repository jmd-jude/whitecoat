import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", "")
)

# Page config
st.set_page_config(
    page_title="WhiteCoat Questionnaire",
    page_icon="📝",
    initial_sidebar_state="expanded"
)

# Check authentication
if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access this page.")
    st.stop()

# Title and introduction
st.title("WhiteCoat Questionnaire")
st.write("Please complete the questionnaire below to assess your current preparation level for medical school applications.")

# Load previous responses if they exist
try:
    responses = supabase.table("questionnaire_responses").select("responses").eq("user_id", st.session_state.user.id).execute()
    if responses.data:
        previous_responses = responses.data[0]["responses"]
    else:
        previous_responses = {}
except Exception as e:
    st.error(f"Error loading previous responses: {str(e)}")
    previous_responses = {}

# Creating the form
with st.form("premed_gap_analysis_form"):
    st.header("I. Research Experience")

    research_hours = st.radio(
        "1. Total research hours across all roles:",
        ["None yet", "0–50 hours", "51–150 hours", "151–300 hours", "301–500 hours", "501–800 hours", "800+ hours"],
        index=["None yet", "0–50 hours", "51–150 hours", "151–300 hours", "301–500 hours", "501–800 hours", "800+ hours"].index(previous_responses.get("research_hours", "None yet"))
    )

    weekly_research_hours = st.radio(
        "2. Average hours spent on research per week:",
        ["0–2 hours", "3–5 hours", "6–10 hours", "11–15 hours", "15+ hours"],
        index=["0–2 hours", "3–5 hours", "6–10 hours", "11–15 hours", "15+ hours"].index(previous_responses.get("weekly_research_hours", "0–2 hours"))
    )

    research_tasks = st.multiselect(
        "3. What type of research tasks do you primarily perform? (Check all that apply)",
        ["Wet Lab Work", "Data Analysis", "Clinical Research", "Literature Reviews or Writing", "Other"],
        default=previous_responses.get("types_of_research_tasks", [])
    )

    led_projects = st.radio(
        "4. Have you independently led any research projects or major initiatives?",
        ["None", "Contributed to a project with leadership components", "Co-led 1 project", "Led 1 project", "Led 2+ projects"],
        index=["None", "Contributed to a project with leadership components", "Co-led 1 project", "Led 1 project", "Led 2+ projects"].index(previous_responses.get("led_projects", "None"))
    )

    research_outputs = st.radio(
        "5. How many research outputs have you contributed to?",
        ["None yet", "1 output", "2–3 outputs", "4–5 outputs", "6+ outputs"],
        index=["None yet", "1 output", "2–3 outputs", "4–5 outputs", "6+ outputs"].index(previous_responses.get("research_outputs", "None yet"))
    )

    st.header("II. Clinical Experience")
    high_school_clinical_hours = st.radio(
        "6. How many clinical hours did you log during high school?",
        ["0–50 hours", "51–100 hours", "101–200 hours", "201–300 hours", "300+ hours"],
        index=["0–50 hours", "51–100 hours", "101–200 hours", "201–300 hours", "300+ hours"].index(previous_responses.get("high_school_clinical_hours", "0–50 hours"))
    )

    post_high_school_clinical_hours = st.radio(
        "7. How many clinical hours have you logged since high school?",
        ["None yet", "0–50 hours", "51–100 hours", "101–300 hours", "301–500 hours", "501–800 hours", "800+ hours"],
        index=["None yet", "0–50 hours", "51–100 hours", "101–300 hours", "301–500 hours", "501–800 hours", "800+ hours"].index(previous_responses.get("post_high_school_clinical_hours", "None yet"))
    )

    patient_interaction = st.radio(
        "8. How much direct patient interaction experience have you gained?",
        ["None yet", "Minimal", "Moderate", "Extensive", "High"],
        index=["None yet", "Minimal", "Moderate", "Extensive", "High"].index(previous_responses.get("patient_interaction", "None yet"))
    )

    clinical_certification = st.radio(
        "9. Are you planning to pursue any clinical certifications?",
        ["No, not planning to pursue certification", "Yes, planning to start within 6 months", "Yes, planning to start within 1 year", "Yes, planning to start within 2 years", "Already certified"],
        index=["No, not planning to pursue certification", "Yes, planning to start within 6 months", "Yes, planning to start within 1 year", "Yes, planning to start within 2 years", "Already certified"].index(previous_responses.get("clinical_certification", "No, not planning to pursue certification"))
    )

    weekly_clinical_hours = st.radio(
        "10. How many hours per week do you anticipate working in a clinical setting?",
        ["Not applicable", "0–5 hours", "6–15 hours", "16–25 hours", "25+ hours"],
        index=["Not applicable", "0–5 hours", "6–15 hours", "16–25 hours", "25+ hours"].index(previous_responses.get("weekly_clinical_hours", "Not applicable"))
    )

    st.header("III. Leadership, Service, and Extracurricular Activities")
    leadership_roles = st.radio(
        "11. How many leadership roles have you held?",
        ["None yet", "1 role", "2–3 roles", "4+ roles"],
        index=["None yet", "1 role", "2–3 roles", "4+ roles"].index(previous_responses.get("leadership_roles", "None yet"))
    )

    service_scale = st.radio(
        "12. How would you describe the scale of your service or volunteer efforts?",
        ["Small-scale", "Moderate-scale", "Large-scale", "Community-wide or organizational-level impact"],
        index=["Small-scale", "Moderate-scale", "Large-scale", "Community-wide or organizational-level impact"].index(previous_responses.get("service_scale", "Small-scale"))
    )

    weekly_volunteer_hours = st.radio(
        "13. How many hours per week do you dedicate to extracurricular activities?",
        ["0–1 hour", "2–3 hours", "4–5 hours", "6–10 hours", "10+ hours"],
        index=["0–1 hour", "2–3 hours", "4–5 hours", "6–10 hours", "10+ hours"].index(previous_responses.get("weekly_volunteer_hours", "0–1 hour"))
    )

    service_outcomes = st.radio(
        "14. Have your service or leadership activities resulted in tangible outcomes?",
        ["None yet", "1–2 outcomes", "3–5 outcomes", "6–10 outcomes", "10+ outcomes"],
        index=["None yet", "1–2 outcomes", "3–5 outcomes", "6–10 outcomes", "10+ outcomes"].index(previous_responses.get("service_outcomes", "None yet"))
    )

    st.header("IV. Academic Readiness")
    academic_preparedness = st.slider(
        "15. How prepared are you to meet the academic expectations of your target schools?",
        1, 5, previous_responses.get("academic_preparedness", 3)
    )

    academic_areas = st.multiselect(
        "16. Which academic area do you feel requires the most immediate improvement?",
        ["Science Prerequisites", "Quantitative Skills", "Study Strategies", "Writing and Communication", "General Education Requirements"],
        default=previous_responses.get("academic_areas", [])
    )

    academic_strengths = st.multiselect(
        "17. What academic strengths or experiences set you apart?",
        ["A strong foundation in biology or chemistry", "Quantitative or data-focused expertise", "Humanities or social sciences focus", "Interdisciplinary focus", "Advanced electives in specialized topics", "Independent study or research projects"],
        default=previous_responses.get("academic_strengths", [])
    )

    mcat_confidence = st.slider(
        "18. How confident are you in preparing for the MCAT by summer/fall 2027?",
        1, 5, previous_responses.get("mcat_confidence", 3)
    )

    gpa_confidence = st.slider(
        "19. How confident are you that your GPA reflects your ability to succeed in medical school?",
        1, 5, previous_responses.get("gpa_confidence", 3)
    )

    st.header("V. Personal Vision and Priorities")
    application_gaps = st.radio(
        "20. What specific gaps or experiences do you believe are missing from your application?",
        ["No concerns currently", "Missing leadership roles", "Limited clinical exposure", "Need more research output", "Lack of service/volunteer work", "Other"],
        index=["No concerns currently", "Missing leadership roles", "Limited clinical exposure", "Need more research output", "Lack of service/volunteer work", "Other"].index(previous_responses.get("application_gaps", "No concerns currently"))
    )

    primary_focus = st.multiselect(
        "21. What is your primary area of focus in your pre-med journey?",
        ["Academic Excellence", "Clinical Experience", "Research Impact", "Leadership and Service", "Specialty Preparation"],
        default=previous_responses.get("primary_focus", [])
    )

    greatest_weakness = st.radio(
        "22. What area of your medical school application do you feel is your greatest weakness?",
        ["Academic Rigor", "Clinical Experience", "Research Impact", "Leadership and Service", "Application Narrative"],
        index=["Academic Rigor", "Clinical Experience", "Research Impact", "Leadership and Service", "Application Narrative"].index(previous_responses.get("greatest_weakness", "Academic Rigor"))
    )

    future_contribution = st.multiselect(
        "23. Where do you see yourself contributing most as a future physician?",
        ["Patient Care", "Research", "Education", "Advocacy", "Leadership"],
        default=previous_responses.get("future_contribution", [])
    )

    application_timing = st.radio(
        "24. What is your flexibility around medical school application timing?",
        ["Firm timeline, must apply in target year", "Somewhat flexible, could delay 1 year if beneficial", "Very flexible, willing to optimize timing", "Already committed to specific gap year activities"],
        index=["Firm timeline, must apply in target year", "Somewhat flexible, could delay 1 year if beneficial", "Very flexible, willing to optimize timing", "Already committed to specific gap year activities"].index(previous_responses.get("application_timing", "Firm timeline, must apply in target year"))
    )

    academic_history = st.multiselect(
        "25. Which of the following applies to your academic history? Select all that apply.",
        ["I have transfer credits from a 4-year institution", "I have transfer credits from a community college", "I have AP/IB credits applied to my transcript", "I have courses completed at international institutions", "I have repeated one or more courses (e.g., due to grade replacement or retakes)", "I have incomplete or pending grades", "My transcript includes non-standard grading systems (e.g., Pass/Fail, percentages, distinctions)", "I followed a non-traditional or accelerated pathway (e.g., dual enrollment, gap years, summer-only courses)", "None of the above (standard academic record)"],
        default=previous_responses.get("academic_history", [])
    )

    # Submit button
    submitted = st.form_submit_button("Submit")
    if submitted:
        try:
            # Collect all form responses
            form_responses = {
                "research_hours": research_hours,
                "weekly_research_hours": weekly_research_hours,
                "types_of_research_tasks": research_tasks,
                "led_projects": led_projects,
                "research_outputs": research_outputs,
                "high_school_clinical_hours": high_school_clinical_hours,
                "post_high_school_clinical_hours": post_high_school_clinical_hours,
                "patient_interaction": patient_interaction,
                "clinical_certification": clinical_certification,
                "weekly_clinical_hours": weekly_clinical_hours,
                "leadership_roles": leadership_roles,
                "service_scale": service_scale,
                "weekly_volunteer_hours": weekly_volunteer_hours,
                "service_outcomes": service_outcomes,
                "academic_preparedness": academic_preparedness,
                "academic_areas": academic_areas,
                "academic_strengths": academic_strengths,
                "mcat_confidence": mcat_confidence,
                "gpa_confidence": gpa_confidence,
                "application_gaps": application_gaps,
                "primary_focus": primary_focus,
                "greatest_weakness": greatest_weakness,
                "future_contribution": future_contribution,
                "application_timing": application_timing,
                "academic_history": academic_history
            }
            
            # Save to Supabase
            data = {
                "user_id": st.session_state.user.id,
                "responses": form_responses
            }
            
            supabase.table("questionnaire_responses").upsert(data).execute()
            
            st.success("Your responses have been saved!")
            
        except Exception as e:
            st.error(f"Error saving responses: {str(e)}")
            st.error("Full error details:")
            st.exception(e)
