import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Set page config
st.set_page_config(page_title="Cohort Comparison", layout="wide")

# Title section with explanation
st.title("SPM Alignment Dashboard")

# Create two columns for the layout
col1, col2 = st.columns([1, 1.5])

with col1:
    # Add custom styling
    st.markdown("""
        <style>
            div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
                background-color: white;
                padding: 2rem;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            .stMarkdown {
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            }
            .stMarkdown h1 {
                font-size: 1.5rem !important;
                margin-bottom: 1.5rem !important;
                color: #1a202c;
            }
            .stMarkdown h2 {
                font-size: 1.25rem !important;
                margin: 1.5rem 0 1rem 0 !important;
                color: #2d3748;
            }
            .stMarkdown p {
                margin-bottom: 0.75rem !important;
                line-height: 1.6 !important;
                color: #4a5568;
            }
            .checkmark {
                color: #38a169;
                font-weight: bold;
                margin-right: 0.5rem;
            }
            .bullet {
                color: #718096;
                margin-right: 0.5rem;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Create container with content
    with st.container():
        st.markdown("<h1>Your Profile Aligns with Clinical-Investigative Schools</h1>", unsafe_allow_html=True)
        
        st.markdown("<h2>Why This Cohort is a Strong Fit for You:</h2>", unsafe_allow_html=True)
        
        # Clinical Experience
        st.markdown('<p><span class="checkmark">✓</span><strong>Clinical Experience</strong> - 300+ patient care hours (medical assistant, COVID-19 volunteer)</p>', unsafe_allow_html=True)
        
        # Research Strength
        st.markdown('<p><span class="checkmark">✓</span><strong>Research Strength</strong> - Advanced lab skills (PCR, Western Blot, microscopy) + manuscript in progress</p>', unsafe_allow_html=True)
        
        # Leadership & Service
        st.markdown('<p><span class="checkmark">✓</span><strong>Leadership & Service</strong> - PreMed Society president, mentoring & leadership impact</p>', unsafe_allow_html=True)
        
        # Academic Rigor
        st.markdown('<p><span class="checkmark">✓</span><strong>Academic Rigor</strong> - 3.85 GPA in challenging coursework</p>', unsafe_allow_html=True)
        
        # Specialty Focus
        st.markdown('<p><span class="checkmark">✓</span><strong>Specialty Focus</strong> - Strong foundation in neurology/oncology research</p>', unsafe_allow_html=True)
        
        st.markdown("<h2>What Clinical-Investigative Schools Prioritize:</h2>", unsafe_allow_html=True)
        
        st.markdown("""
        <p><span class="bullet">•</span>Interdisciplinary research & clinical trials</p>
        <p><span class="bullet">•</span>Bridging patient care with scientific discovery</p>
        <p><span class="bullet">•</span><strong>Example Schools:</strong> Duke, Mount Sinai, USC Keck</p>
        """, unsafe_allow_html=True)

with col2:
    # Create dataframe
    data = {
        'Metric': ['Clinical Experience', 'Technical Skills', 'Leadership & Service', 
                'Research Activities', 'Academic Rigor', 'Specialty Preparation'],
        'Mission-Driven': [81, 64, 85, 75, 72, 93],
        'Patient-Centered': [81, 86, 79, 89, 76, 82],
        'Community-Clinical': [96, 69, 70, 88, 96, 90],
        'Clinical-Investigative': [71, 92, 88, 78, 93, 85],
        'Research-Intensive': [74, 80, 73, 71, 62, 77],
        'Pre-Med': [45, 90, 65, 75, 98, 80]
    }

    df = pd.DataFrame(data)

    # Create radio button for cohort selection
    selected_cohort = st.radio(
        "Select Cohort for Comparison:",
        ['Mission-Driven', 'Patient-Centered', 'Community-Clinical', 'Clinical-Investigative', 'Research-Intensive']
    )

    # Create radar chart
    categories = data['Metric']

    fig = go.Figure()

    # Add selected cohort trace
    fig.add_trace(go.Scatterpolar(
        r=df[selected_cohort],
        theta=categories,
        fill='toself',
        name=selected_cohort,
        opacity=0.5,
        line=dict(color='#1f77b4')  # Light blue
    ))

    # Add Pre-Med trace
    fig.add_trace(go.Scatterpolar(
        r=df['Pre-Med'],
        theta=categories,
        fill='toself',
        name='Pre-Med',
        opacity=0.5,
        line=dict(color='#ff9999')  # Light red
    ))

    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        height=600,
        margin=dict(t=0, b=0)  # Reduce margins
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
