# pages/C_Tech_Transfer_Hub.py

import streamlit as st
import pandas as pd
import plotly.figure_factory as ff

from utils import generate_tech_transfer_data

st.set_page_config(page_title="Tech Transfer Hub | Avidity", layout="wide")

st.title("🚀 Technology Transfer Hub")
st.markdown("### Tracking the end-to-end transfer of Avidity's AOC processes to new CDMO facilities.")

# --- Data ---
df = generate_tech_transfer_data()
df['Variance (Days)'] = df['Actual Duration (Days)'].fillna(0) - df['Planned Duration (Days)']

# --- KPIs ---
st.header("Project Health: AOC-1044 Transfer to Lonza")
total_duration = df['Planned Duration (Days)'].sum()
schedule_variance = df['Variance (Days)'].sum()
completed_tasks = df['Actual Duration (Days)'].notna().sum()
total_tasks = len(df)

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Overall Schedule Variance", f"{schedule_variance} Days", delta_color="inverse")
kpi2.metric("Task Completion", f"{completed_tasks} / {total_tasks}")
kpi3.metric("Planned Duration", f"{total_duration} Days")
st.divider()

# --- Critical Path Gantt Chart ---
st.header("Critical Path Analysis")
st.caption("Gantt chart showing task durations, dependencies, and schedule variance. Red tasks are behind schedule.")

# Color tasks based on variance
def get_task_color(variance):
    if pd.isna(variance): return 'rgb(128, 128, 128)' # Grey for planned
    if variance > 0: return 'rgb(218, 41, 28)' # Red for delayed
    return 'rgb(0, 63, 135)' # Blue for on-time/ahead

colors = [get_task_color(v) for v in df['Variance (Days)']]

# Create the Gantt chart using Figure Factory
fig = ff.create_gantt(
    df.rename(columns={'Task ID': 'Task', 'Start Date': 'Start', 'Finish Date': 'Finish'}),
    index_col='Task',
    colors=colors,
    show_colorbar=False,
    group_tasks=True,
    showgrid_x=True,
    title="Tech Transfer Project Timeline"
)

# Add annotations for variance
for i, row in df.iterrows():
    if pd.notna(row['Variance (Days)']) and row['Variance (Days)'] != 0:
        fig.add_annotation(
            x=row['Finish Date'], y=i,
            text=f"{row['Variance (Days):+g']}d",
            showarrow=False, xshift=25,
            font=dict(color="red" if row['Variance (Days)'] > 0 else "green")
        )

st.plotly_chart(fig, use_container_width=True)
