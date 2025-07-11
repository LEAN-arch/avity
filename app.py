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
    fig.add_annotation(x=x_range[1], y=y_range[1], text="<b>Strategic Partners</b><br>Reliable & High Quality", showarrow=False, xanchor='right', yanchor='top', font=dict(color='green'))
    fig.add_annotation(x=x_range[0], y=y_range[1], text="<b>Quality Focus</b><br>High Quality, Delivery Risk", showarrow=False, xanchor='left', yanchor='top', font=dict(color='orange'))
    fig.add_annotation(x=x_range[0], y=y_range[0], text="<b>High Concern</b><br>Performance Plans Needed", showarrow=False, xanchor='left', yanchor='bottom', font=dict(color='red'))
    fig.add_annotation(x=x_range[1], y=y_range[0], text="<b>Inconsistent</b><br>Reliable, Quality Varies", showarrow=False, xanchor='right', yanchor='bottom', font=dict(color='orange'))
    fig.update_layout(height=450, xaxis_title="On-Time Delivery (%)", yaxis_title="Quality Score (Composite)", plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=40, l=40, r=20), xaxis=dict(range=x_range), yaxis=dict(range=y_range), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Methodology & Actionability: Performance Quadrant"):
        st.markdown("""
        **Methodology:** This is a 2x2 matrix, a powerful business analysis tool for strategic segmentation. It plots each CDMO based on two critical performance dimensions: operational reliability (X-axis) and a composite quality score (Y-axis). Additional dimensions are encoded using bubble size (production volume) and color (average process yield). The quadrant lines are dynamically placed at the portfolio's mean performance, allowing for relative assessment.

        **Significance & Insights:**
        - **Top-Right (Strategic Partners):** High reliability and quality. These are your best partners.
        - **Top-Left (Quality Focus):** High quality but struggle with timeliness, suggesting logistical or scheduling challenges rather than technical ones.
        - **Bottom-Right (Delivery Focus):** Reliable delivery but inconsistent quality, pointing to potential issues with process control or deviation management.
        - **Bottom-Left (High Concern):** Underperform on both axes. A large bubble here represents a major portfolio risk.

        **Managerial Actionability:**
        - **Action:** Engage "High Concern" partners with a formal Performance Improvement Plan (PIP).
        - **Action:** Work with "Quality Focus" partners on logistics and scheduling.
        - **Action:** Launch technical deep-dives with "Delivery Focus" partners to improve process control.
        - **Action:** Nurture and reward "Strategic Partners" with new, high-value projects.
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

    with st.expander("Methodology & Actionability: Treemap"):
        st.markdown("""
        **Methodology:** A treemap is a space-filling visualization for hierarchical data. It uses nested rectangles where the area of each rectangle is directly proportional to its value (here, the count of batches).

        **Significance & Insights:** The chart instantly reveals concentration. You can see in seconds which **Program** (e.g., DM1) constitutes the largest portion of the manufacturing workload, which **CDMO** is responsible for the most batches, and crucially, how the **risk** (At Risk/Failed batches) is distributed across them.

        **Managerial Actionability:**
        - **Action:** If a large rectangle representing a key program contains significant red or maroon sub-rectangles (At Risk/Failed), this is a critical supply risk requiring immediate escalation and the formation of a dedicated task force.
        - **Action:** Use this to justify resource allocation. The largest program areas should have the most robust oversight and support.
        """)
