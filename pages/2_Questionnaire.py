import streamlit as st

# Title and introduction
st.title("Pre-Med Gap Analysis Questionnaire")
st.write("Please complete the questionnaire below to assess your current preparation level for medical school applications.")

# Creating the form
with st.form("premed_gap_analysis_form"):
    st.header("I. Research Experience")

    research_hours = st.radio(
        "1. Total research hours across all roles:",
        ["None yet", "0–50 hours", "51–150 hours", "151–300 hours", "301–500 hours", "501–800 hours", "800+ hours"]
    )

    weekly_research_hours = st.radio(
        "2. Average hours spent on research per week:",
        ["0–2 hours", "3–5 hours", "6–10 hours", "11–15 hours", "15+ hours"]
    )

    research_tasks = st.multiselect(
        "3. What type of research tasks do you primarily perform? (Check all that apply)",
        ["Wet Lab Work", "Data Analysis", "Clinical Research", "Literature Reviews or Writing", "Other"]
    )

    led_projects = st.radio(
        "4. Have you independently led any research projects or major initiatives?",
        ["None", "Contributed to a project with leadership components", "Co-led 1 project", "Led 1 project", "Led 2+ projects"]
    )

    research_outputs = st.radio(
        "5. How many research outputs have you contributed to?",
        ["None yet", "1 output", "2–3 outputs", "4–5 outputs", "6+ outputs"]
    )

    st.header("II. Clinical Experience")
    high_school_clinical_hours = st.radio(
        "6. How many clinical hours did you log during high school?",
        ["0–50 hours", "51–100 hours", "101–200 hours", "201–300 hours", "300+ hours"]
    )

    post_high_school_clinical_hours = st.radio(
        "7. How many clinical hours have you logged since high school?",
        ["None yet", "0–50 hours", "51–100 hours", "101–300 hours", "301–500 hours", "501–800 hours", "800+ hours"]
    )

    patient_interaction = st.radio(
        "8. How much direct patient interaction experience have you gained?",
        ["None yet", "Minimal", "Moderate", "Extensive", "High"]
    )

    clinical_certification = st.radio(
        "9. Are you planning to pursue any clinical certifications?",
        ["No, not planning to pursue certification", "Yes, planning to start within 6 months", "Yes, planning to start within 1 year", "Yes, planning to start within 2 years", "Already certified"]
    )

    weekly_clinical_hours = st.radio(
        "10. How many hours per week do you anticipate working in a clinical setting?",
        ["Not applicable", "0–5 hours", "6–15 hours", "16–25 hours", "25+ hours"]
    )

    st.header("III. Leadership, Service, and Extracurricular Activities")
    leadership_roles = st.radio(
        "11. How many leadership roles have you held?",
        ["None yet", "1 role", "2–3 roles", "4+ roles"]
    )

    service_scale = st.radio(
        "12. How would you describe the scale of your service or volunteer efforts?",
        ["Small-scale", "Moderate-scale", "Large-scale", "Community-wide or organizational-level impact"]
    )

    weekly_volunteer_hours = st.radio(
        "13. How many hours per week do you dedicate to extracurricular activities?",
        ["0–1 hour", "2–3 hours", "4–5 hours", "6–10 hours", "10+ hours"]
    )

    service_outcomes = st.radio(
        "14. Have your service or leadership activities resulted in tangible outcomes?",
        ["None yet", "1–2 outcomes", "3–5 outcomes", "6–10 outcomes", "10+ outcomes"]
    )

    st.header("IV. Academic Readiness")
    academic_preparedness = st.slider("15. How prepared are you to meet the academic expectations of your target schools?", 1, 5, 3)

    academic_areas = st.multiselect(
        "16. Which academic area do you feel requires the most immediate improvement?",
        ["Science Prerequisites", "Quantitative Skills", "Study Strategies", "Writing and Communication", "General Education Requirements"]
    )

    academic_strengths = st.multiselect(
        "17. What academic strengths or experiences set you apart?",
        ["A strong foundation in biology or chemistry", "Quantitative or data-focused expertise", "Humanities or social sciences focus", "Interdisciplinary focus", "Advanced electives in specialized topics", "Independent study or research projects"]
    )

    mcat_confidence = st.slider("18. How confident are you in preparing for the MCAT by summer/fall 2027?", 1, 5, 3)
    gpa_confidence = st.slider("19. How confident are you that your GPA reflects your ability to succeed in medical school?", 1, 5, 3)

    st.header("V. Personal Vision and Priorities")
    application_gaps = st.radio(
        "20. What specific gaps or experiences do you believe are missing from your application?",
        ["No concerns currently", "Missing leadership roles", "Limited clinical exposure", "Need more research output", "Lack of service/volunteer work", "Other"]
    )

    primary_focus = st.multiselect(
        "21. What is your primary area of focus in your pre-med journey?",
        ["Academic Excellence", "Clinical Experience", "Research Impact", "Leadership and Service", "Specialty Preparation"]
    )

    greatest_weakness = st.radio(
        "22. What area of your medical school application do you feel is your greatest weakness?",
        ["Academic Rigor", "Clinical Experience", "Research Impact", "Leadership and Service", "Application Narrative"]
    )

    future_contribution = st.multiselect(
        "23. Where do you see yourself contributing most as a future physician?",
        ["Patient Care", "Research", "Education", "Advocacy", "Leadership"]
    )

    application_timing = st.radio(
        "24. What is your flexibility around medical school application timing?",
        ["Firm timeline, must apply in target year", "Somewhat flexible, could delay 1 year if beneficial", "Very flexible, willing to optimize timing", "Already committed to specific gap year activities"]
    )

    # Submit button
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.success("Your responses have been recorded. Thank you for completing the questionnaire!")
