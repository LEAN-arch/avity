# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import generate_cdmo_data, generate_master_schedule

st.set_page_config(
    page_title="External Manufacturing Command Center | Avidity",
    page_icon="https://www.aviditybiosciences.com/wp-content/uploads/2022/02/cropped-Avidity-Favicon-32x32.png",
    layout="wide"
)

# --- Data Loading ---
cdmo_df = generate_cdmo_data()
schedule_df = generate_master_schedule()

# --- Header ---
st.image("https://www.aviditybiosciences.com/wp-content/uploads/2024/02/Avidity-logo-1.svg", width=250)
st.title("External Manufacturing Command Center")
st.markdown("### Strategic & Technical Oversight of Avidity's Global CDMO Network and AOC Supply Chain")

# --- TECHNICAL KPIs ---
st.header("Portfolio Performance: Key Technical Indicators")
total_batches = len(schedule_df)
schedule_df['Cycle Time Variance (Days)'] = schedule_df['Actual Cycle Time (Days)'] - schedule_df['Planned Cycle Time (Days)']
avg_cycle_time_variance = schedule_df['Cycle Time Variance (Days)'].mean()
shipped_batches = schedule_df[schedule_df['Status'] == 'Shipped']
right_first_time = (1 - (shipped_batches['Deviation ID'].notna().sum() / len(shipped_batches))) * 100 if not shipped_batches.empty else 100
active_cdmos = cdmo_df[cdmo_df['Status'] == 'Active'].shape[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Active CDMOs", active_cdmos, help="Number of currently active manufacturing partners.")
col2.metric("Right First Time (RFT)", f"{right_first_time:.1f}%", help="Percentage of completed batches shipped without a deviation.")
col3.metric("Avg. Cycle Time Variance", f"{avg_cycle_time_variance:.1f} Days", help="Positive value indicates batches are taking longer than planned.", delta_color="inverse")
col4.metric("Batches At Risk / Failed", schedule_df[schedule_df['Status'].isin(['At Risk', 'Failed'])].shape[0], help="Total count of batches currently at risk or failed.")
st.divider()

# --- Main Visualizations ---
st.header("Portfolio Overview: Performance & Production Volume")
col_quad, col_treemap = st.columns(2)

with col_quad:
    st.subheader("CDMO Performance Quadrant")
    avg_otd = cdmo_df['Avg. On-Time Delivery (%)'].mean()
    avg_quality = cdmo_df['Quality Score (1-100)'].mean()
    x_range = [cdmo_df['Avg. On-Time Delivery (%)'].min() - 5, 102]
    y_range = [cdmo_df['Quality Score (1-100)'].min() - 5, 102]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cdmo_df['Avg. On-Time Delivery (%)'], y=cdmo_df['Quality Score (1-100)'],
        text=cdmo_df['CDMO Name'], mode='markers+text',
        marker=dict(size=cdmo_df['Batches YTD'] * 2.5, color=cdmo_df['Avg. Yield (%)'], colorscale='Viridis', showscale=True, colorbar=dict(title='Avg. Yield')),
        textposition="top center", textfont=dict(size=12)
    ))
    fig.add_vline(x=avg_otd, line_dash="dash", line_color="grey")
    fig.add_hline(y=avg_quality, line_dash="dash", line_color="grey")
    fig.add_annotation(x=x_range[1], y=y_range[1], text="<b>Strategic Partners</b><br>High Quality & Reliable", showarrow=False, xanchor='right', yanchor='top', font=dict(color='green'))
    fig.add_annotation(x=x_range[0], y=y_range[1], text="<b>Quality Focus</b><br>High Quality, Delivery Risk", showarrow=False, xanchor='left', yanchor='top', font=dict(color='orange'))
    fig.add_annotation(x=x_range[0], y=y_range[0], text="<b>High Concern</b><br>Performance Plans Needed", showarrow=False, xanchor='left', yanchor='bottom', font=dict(color='red'))
    fig.add_annotation(x=x_range[1], y=y_range[0], text="<b>Delivery Focus</b><br>Reliable, Quality Varies", showarrow=False, xanchor='right', yanchor='bottom', font=dict(color='orange'))
    fig.update_layout(height=450, xaxis_title="On-Time Delivery (%)", yaxis_title="Quality Score (Composite)", plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=40, l=40, r=20), xaxis=dict(range=x_range), yaxis=dict(range=y_range), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("What is the Performance Quadrant?"):
        st.markdown("""
        **What it is:** This chart plots each CDMO based on two key axes: operational reliability (On-Time Delivery) and product quality (a composite score including success rate and deviation frequency). The size of each bubble represents the volume of batches produced this year.
        
        **What it tells you:** It provides a rapid strategic assessment of the entire CDMO network.
        - **Top-Right (Strategic Partners):** These are your best-performing partners. Leverage and protect these relationships.
        - **Bottom-Left (High Concern):** These partners are underperforming on both fronts and require immediate and intensive management focus.
        
        **Actionability:** Use this chart to prioritize your management efforts. A large bubble in a poor quadrant (e.g., WuXi) is a major portfolio risk that needs immediate attention.
        """)

with col_treemap:
    st.subheader("Production Volume by Program & CDMO")
    fig = px.treemap(
        schedule_df,
        path=[px.Constant("All Programs"), 'Program', 'CDMO', 'Status'],
        title="Batch Distribution Across Portfolio",
        color_discrete_map={
            '(?)':'#2ca02c', 'DM1':'#003F87', 'DMD':'#00AEEF', 'FSHD':'#8DC63F',
            'Catalent Pharma':'#F37021', 'WuXi Biologics':'#662D91',
            'At Risk':'red', 'Failed':'maroon'
            }
    )
    fig.update_layout(height=450, margin = dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("What is the Treemap?"):
        st.markdown("""
        **What it is:** This chart visualizes the composition of your production portfolio. The size of each rectangle represents the number of batches in that category.
        
        **What it tells you:** It shows where your production volume and risk are concentrated. You can quickly see which programs (e.g., DM1) and which CDMOs dominate your manufacturing activities.
        
        **Actionability:** A large red or maroon area (At Risk/Failed) within a key program or CDMO highlights a significant, concentrated risk to supply. Click on the rectangles to drill down and explore the data hierarchy.
        """)
