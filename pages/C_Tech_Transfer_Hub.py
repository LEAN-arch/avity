# pages/C_Tech_Transfer_Hub.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import generate_tech_transfer_data
from datetime import datetime, timedelta

st.set_page_config(page_title="Tech Transfer Hub | Avidity", layout="wide")
st.title("🚀 Technology Transfer Hub")
st.markdown("### Managing the end-to-end transfer of Avidity's AOC processes to new CDMO facilities.")

# --- Data Preparation ---
df = generate_tech_transfer_data()
df['Actual Finish Date'] = df.apply(
    lambda row: row['Start Date'] + timedelta(days=row['Actual Duration (Days)']) if pd.notna(row['Actual Duration (Days)']) else pd.NaT,
    axis=1
)
df['Variance (Days)'] = (df['Actual Finish Date'] - df['Finish Date']).dt.days.fillna(0)

# --- KPIs ---
st.header("Project Health: AOC-1044 Transfer to Lonza")
total_duration = df['Planned Duration (Days)'].sum()
project_finish_date = max(df['Actual Finish Date'].max(), df['Finish Date'].max())
schedule_variance = (project_finish_date - df['Finish Date'].max()).days
completed_tasks = df['Progress (%)'].eq(100).sum()
total_tasks = len(df)

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Overall Schedule Variance", f"{schedule_variance} Days", delta=f"{schedule_variance} Days vs Plan", delta_color="inverse")
kpi2.metric("Task Completion", f"{completed_tasks} / {total_tasks}", f"{completed_tasks/total_tasks:.0%} Complete")
kpi3.metric("Planned Duration", f"{total_duration} Days")
st.divider()

# --- Custom Gantt Chart ---
st.header("Interactive Project Gantt Chart")
st.caption("Color indicates task risk level. Progress is shown within each bar. Hover for full details.")

# --- START: FIX for Milestone Diamond Colors ---
# Define colors based on risk
risk_colors = {'High': '#DC3912', 'Medium': '#FF9900', 'Low': '#109618'}

# Update the manual legend to be more precise
st.write(f"""
**Legend:** Task bar and milestone diamond (<span style="color:black;">♦</span>) colors indicate risk level:  
<span style="background-color:{risk_colors['High']}; padding: 2px 10px; border-radius: 5px; color: white;">High Risk</span>  
<span style="background-color:{risk_colors['Medium']}; padding: 2px 10px; border_radius: 5px; color: white;">Medium Risk</span>  
<span style="background-color:{risk_colors['Low']}; padding: 2px 10px; border_radius: 5px; color: white;">Low Risk</span>
""", unsafe_allow_html=True)


fig = go.Figure()

# Add traces for each task
for i, task in df.iterrows():
    # Background bar for the full planned task
    fig.add_trace(go.Bar(
        x=[task['Planned Duration (Days)']], y=[task['Task']], orientation='h',
        base=[task['Start Date']], marker_color='#E0E0E0',
        hoverinfo='none', showlegend=False,
    ))
    
    # Foreground bar for the progress
    progress_duration = task['Planned Duration (Days)'] * (task['Progress (%)'] / 100)
    fig.add_trace(go.Bar(
        x=[progress_duration], y=[task['Task']], orientation='h',
        base=[task['Start Date']], marker_color=risk_colors[task['Risk Level']],
        text=f"{task['Progress (%)']}%", textposition='inside', insidetextanchor='middle',
        showlegend=False,
        hovertext=(
            f"<b>{task['Task']}</b><br>"
            f"Lead Team: {task['Lead Team']}<br>"
            f"Risk: {task['Risk Level']}<br>"
            f"Status: {task['Progress (%)']}% Complete<br>"
            f"Planned: {task['Start Date'].strftime('%b %d')} - {task['Finish Date'].strftime('%b %d')} ({task['Planned Duration (Days)']}d)<br>"
            f"Variance: {task['Variance (Days)']:+.0f}d"
        ),
        hoverinfo='text'
    ))

# Create a list of colors for the milestone markers based on risk level
milestone_colors = df['Risk Level'].map(risk_colors).tolist()

# Add milestone markers with risk-based colors
fig.add_trace(go.Scatter(
    x=df['Finish Date'],
    y=df['Task'],
    mode='markers',
    marker=dict(
        symbol='diamond',
        size=14,
        color=milestone_colors, # Use the list of colors
        line=dict(width=1, color='DarkSlateGray') # Add a border for visibility
    ),
    name='Planned Finish',
    hoverinfo='none',
    showlegend=False
))
# --- END: FIX for Milestone Diamond Colors ---

# Today line
today = datetime.today()
fig.add_shape(type='line', x0=today, y0=-0.5, x1=today, y1=len(df)-0.5, line=dict(color='grey', width=2, dash='dash'))
fig.add_annotation(x=today, y=len(df)-0.5, text="Today", showarrow=False, xshift=10, yshift=10, font=dict(color="grey"))

# Layout settings
chart_height = len(df) * 40 + 150
fig.update_layout(
    title='Tech Transfer Project Timeline & Progress',
    xaxis_title='Timeline', yaxis_title=None, barmode='overlay', height=chart_height, showlegend=False,
    yaxis=dict(autorange="reversed", tickfont=dict(size=12)),
    xaxis=dict(type='date', tickformat='%b %Y', gridcolor='LightGray'),
    plot_bgcolor='white', margin=dict(l=10, r=10, t=50, b=50)
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("How to Interpret this Gantt Chart"):
    st.markdown("""
    **What it is:** This is a professional project management chart showing the timeline, progress, and risk for each task in the tech transfer project.
    **How to Read It:**
    - **Y-Axis:** Lists all project tasks.
    - **X-Axis:** The project timeline.
    - **Gray Background Bar:** Represents the full planned duration of the task.
    - **Colored Foreground Bar:** Represents the actual progress. The length shows how much is complete, and the color indicates the task's inherent risk level.
    - **Colored Diamond (<span style="color:black;">♦</span>):** Marks the planned completion date (milestone). **Its color also indicates the task's risk level.**
    - **Gray Dashed Line:** Indicates today's date for context.
    **Actionability:**
    - **Focus on Red:** Immediately identify **High Risk** tasks by their red bars and red diamonds.
    - **Check Progress vs. Today:** Pay close attention to any task where the colored progress bar has not yet crossed the "Today" line, especially if it's a high-risk task. This indicates it is behind schedule and requires immediate managerial intervention.
    - **Hover for Details:** Get all the critical data for any task instantly by hovering over its bar.
    """)
