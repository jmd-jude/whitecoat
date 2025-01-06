import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Set page config
st.set_page_config(page_title="Cohort Comparison", layout="wide")
st.title("Cohort Comparison Dashboard")

# Create dataframe
data = {
    'Metric': ['Clinical Exposure', 'Technical Skills', 'Service & Leadership', 
               'Research', 'Academic Rigor', 'Specialty Preparation'],
    'Cohort A': [81, 64, 85, 75, 72, 93],
    'Cohort B': [81, 86, 79, 89, 76, 82],
    'Cohort C': [96, 69, 70, 88, 96, 90],
    'Cohort D': [71, 92, 88, 78, 93, 85],
    'Cohort E': [74, 80, 73, 71, 62, 77],
    'Lucia': [45, 90, 65, 75, 98, 80]
}

df = pd.DataFrame(data)

# Create radio button for cohort selection
selected_cohort = st.radio(
    "Select Cohort for Comparison:",
    ['Cohort A', 'Cohort B', 'Cohort C', 'Cohort D', 'Cohort E']
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
    line=dict(color='#1f77b4')  # Standard blue
))

# Add Lucia's trace (change to a different color)
fig.add_trace(go.Scatterpolar(
    r=df['Lucia'],
    theta=categories,
    fill='toself',
    name='Lucia',
    opacity=0.5,
    line=dict(color='#d62728')  # Change to red
    # Alternative colors you could try:
    # '#2ca02c' for green
    # '#ff7f0e' for orange
    # '#9467bd' for purple
))

# Update layout
fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100]
        )),
    showlegend=True,
    height=800
)

# Display the chart
st.plotly_chart(fig, use_container_width=True)