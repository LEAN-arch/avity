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
overall_yield = schedule_df['Yield (%)'].mean()
batch_success_rate = (1 - (len(schedule_df[schedule_df['Status'] == 'Failed']) / total_batches)) * 100 if total_batches > 0 else 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Overall Batch Success Rate", f"{batch_success_rate:.1f}%", help="Percentage of all batches that met all specifications without failure.")
col2.metric("Avg. Cycle Time Variance", f"{avg_cycle_time_variance:.1f} Days", help="Positive value indicates batches are taking longer than planned.", delta_color="inverse")
col3.metric("Portfolio Avg. Yield", f"{overall_yield:.1f}%", help="Average final yield across all completed batches.")
col4.metric("Active Production Batches", schedule_df[schedule_df['Status'] == 'In Production'].shape[0])
st.divider()


# --- Main Visualizations ---
col_quad, col_gantt = st.columns([1, 2])

with col_quad:
    st.subheader("CDMO Performance Quadrant")
    st.caption("On-Time Delivery vs. Batch Success Rate. Bubble size represents production volume.")
    
    fig = go.Figure()
    # Add quadrant background colors
    fig.add_shape(type="rect", xref="paper", yref="paper", x0=0.5, y0=0.5, x1=1, y1=1, fillcolor="rgba(141, 198, 63, 0.1)", line_width=0, layer="below") # Top Right - Green
    fig.add_shape(type="rect", xref="paper", yref="paper", x0=0, y0=0.5, x1=0.5, y1=1, fillcolor="rgba(243, 112, 33, 0.1)", line_width=0, layer="below") # Top Left - Orange
    fig.add_shape(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=0.5, fillcolor="rgba(218, 41, 28, 0.1)", line_width=0, layer="below") # Bottom half - Red

    # Add scatter plot (bubbles)
    fig.add_trace(go.Scatter(
        x=cdmo_df['Avg. On-Time Delivery (%)'],
        y=cdmo_df['Avg. Batch Success Rate (%)'],
        text=cdmo_df['CDMO Name'],
        mode='markers+text',
        marker=dict(
            size=cdmo_df['Batches YTD'] * 2,  # Scale bubble size
            color=cdmo_df['Avg. Yield (%)'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Avg. Yield')
        ),
        textposition="top center"
    ))
    
    avg_otd = cdmo_df['Avg. On-Time Delivery (%)'].mean()
    avg_bsr = cdmo_df['Avg. Batch Success Rate (%)'].mean()
    
    fig.add_vline(x=avg_otd, line_dash="dash", annotation_text="Avg. OTD")
    fig.add_hline(y=avg_bsr, line_dash="dash", annotation_text="Avg. Success")

    fig.update_layout(
        height=500,
        xaxis_title="On-Time Delivery (%)",
        yaxis_title="Batch Success Rate (%)",
        margin=dict(t=20, b=40, l=40, r=20),
        xaxis=dict(range=[cdmo_df['Avg. On-Time Delivery (%)'].min()-5, cdmo_df['Avg. On-Time Delivery (%)'].max()+5]),
        yaxis=dict(range=[cdmo_df['Avg. Batch Success Rate (%)'].min()-5, 101])
    )
    st.plotly_chart(fig, use_container_width=True)

with col_gantt:
    st.subheader("Master Production Schedule & Deviations")
    st.caption("Timeline of all active and planned batches across the network. Red indicates a deviation.")
    fig = px.timeline(
        schedule_df,
        x_start="Start Date",
        x_end="End Date",
        y="CDMO",
        color="Status",
        hover_name="Batch ID",
        hover_data={"Status": True, "Product": True, "Deviation ID": True},
        title="Production & Release Timeline by Status",
        color_discrete_map={
            'In Production': '#00AEEF',
            'Awaiting Release': '#8DC63F',
            'Shipped': '#003F87',
            'At Risk': '#F37021',
            'Delayed': '#DA291C',
            'Planned': 'grey'
        }
    )
    fig.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.info("This dashboard provides a real-time, technical overview of the entire external manufacturing portfolio. Use the pages in the sidebar to perform deep-dive analyses into specific CDMOs, financials, or projects.")
