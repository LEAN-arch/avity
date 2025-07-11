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

# --- START: Overhauled CDMO Performance Quadrant ---
with col_quad:
    st.subheader("CDMO Performance Quadrant")
    st.caption("On-Time Delivery vs. Batch Success Rate. Bubble size is production volume.")
    
    avg_otd = cdmo_df['Avg. On-Time Delivery (%)'].mean()
    avg_bsr = cdmo_df['Avg. Batch Success Rate (%)'].mean()
    
    # Define generous axis ranges to ensure nothing is clipped
    x_range = [cdmo_df['Avg. On-Time Delivery (%)'].min() - 10, 102]
    y_range = [cdmo_df['Avg. Batch Success Rate (%)'].min() - 10, 102]
    
    fig = go.Figure()
    
    # Add scatter plot (bubbles) first, so they are on the bottom layer
    fig.add_trace(go.Scatter(
        x=cdmo_df['Avg. On-Time Delivery (%)'],
        y=cdmo_df['Avg. Batch Success Rate (%)'],
        text=cdmo_df['CDMO Name'],
        mode='markers+text',
        marker=dict(
            size=cdmo_df['Batches YTD'] * 2.5,
            color=cdmo_df['Avg. Yield (%)'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Avg. Yield')
        ),
        textposition="top center",
        textfont=dict(size=12)
    ))
    
    # Add average lines
    fig.add_vline(x=avg_otd, line_dash="dash", line_color="grey")
    fig.add_hline(y=avg_bsr, line_dash="dash", line_color="grey")
    
    # --- Add Explicit Quadrant Labels for Clarity ---
    fig.add_annotation(x=x_range[1], y=y_range[1], text="<b>High Performers</b><br>Reliable & High Quality", showarrow=False, xanchor='right', yanchor='top', font=dict(color='green'))
    fig.add_annotation(x=x_range[0], y=y_range[1], text="<b>Workhorses</b><br>Good Quality, Delivery Risk", showarrow=False, xanchor='left', yanchor='top', font=dict(color='orange'))
    fig.add_annotation(x=x_range[0], y=y_range[0], text="<b>High Concern</b><br>Quality & Delivery Issues", showarrow=False, xanchor='left', yanchor='bottom', font=dict(color='red'))
    fig.add_annotation(x=x_range[1], y=y_range[0], text="<b>Inconsistent</b><br>Reliable Delivery, Quality Varies", showarrow=False, xanchor='right', yanchor='bottom', font=dict(color='orange'))

    # Add repositioned average line labels
    fig.add_annotation(x=avg_otd, y=y_range[0], text="Avg. OTD", showarrow=False, yanchor='bottom', yshift=5)
    fig.add_annotation(y=avg_bsr, x=x_range[0], text="Avg. Success", showarrow=False, xanchor='left', xshift=5)
    
    fig.update_layout(
        title_text="CDMO On-Time Delivery vs. Quality",
        height=520,
        xaxis_title="On-Time Delivery (%)",
        yaxis_title="Batch Success Rate (%)",
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=40, l=40, r=20),
        xaxis=dict(range=x_range),
        yaxis=dict(range=y_range),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
# --- END: Overhauled CDMO Performance Quadrant ---


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
