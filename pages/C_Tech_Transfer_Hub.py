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

# Prepare a clean DataFrame specifically for Figure Factory
gantt_df = df.copy()
gantt_df = gantt_df.drop(columns=['Task'])
gantt_df = gantt_df.rename(columns={
    'Task ID': 'Task',
    'Start Date': 'Start',
    'Finish Date': 'Finish'
})

# Color tasks based on variance from the original DataFrame
def get_task_color(variance):
    if pd.isna(variance): return 'rgb(128, 128, 128)' # Grey for planned
    if variance > 0: return 'rgb(218, 41, 28)' # Red for delayed
    return 'rgb(0, 63, 135)' # Blue for on-time/ahead

colors = [get_task_color(v) for v in df['Variance (Days)']]

# Create the Gantt chart using the cleaned gantt_df
fig = ff.create_gantt(
    gantt_df,
    index_col='Lead Team',
    colors=colors,
    show_colorbar=False,
    group_tasks=True,
    showgrid_x=True,
    title="Tech Transfer Project Timeline"
)

# --- START: FIX for KeyError ---
# Add annotations for variance using the original 'df' for easier data access
for i, row in df.iterrows():
    if pd.notna(row['Variance (Days)']) and row['Variance (Days)'] != 0:
        # First, get the value from the Series
        variance_val = row['Variance (Days)']
        # Then, apply the f-string formatting to the variable
        variance_text = f"{variance_val:+g}d"
        
        finish_date = row['Start Date'] + pd.to_timedelta(row['Actual Duration (Days)'], unit='d')
        fig.add_annotation(
            x=finish_date, y=i,
            text=variance_text, # Use the formatted text
            showarrow=False, xshift=25,
            font=dict(color="red" if variance_val > 0 else "green")
        )
# --- END: FIX for KeyError ---

st.plotly_chart(fig, use_container_width=True)
