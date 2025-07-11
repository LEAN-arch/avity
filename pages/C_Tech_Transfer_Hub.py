# pages/C_Tech_Transfer_Hub.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from utils import generate_tech_transfer_data

st.set_page_config(page_title="Tech Transfer Hub | Avidity", layout="wide")
st.title("🚀 Technology Transfer Hub")
st.markdown("### Managing the end-to-end transfer of Avidity's AOC processes to new CDMO facilities.")

df = generate_tech_transfer_data()
df['Variance (Days)'] = df['Actual Duration (Days)'].fillna(0) - df['Planned Duration (Days)']

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

st.header("Project Schedule & Risk Analysis")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Critical Path Gantt Chart")
    gantt_df = df.copy().drop(columns=['Task']).rename(columns={'Task ID': 'Task','Start Date': 'Start','Finish Date': 'Finish'})
    def get_task_color(variance):
        if pd.isna(variance): return 'rgb(128, 128, 128)'
        if variance > 0: return 'rgb(218, 41, 28)'
        return 'rgb(0, 63, 135)'
    colors = [get_task_color(v) for v in df['Variance (Days)']]
    fig = ff.create_gantt(gantt_df, index_col='Lead Team', colors=colors, show_colorbar=False, group_tasks=True, showgrid_x=True, title="Tech Transfer Project Timeline")
    for i, row in df.iterrows():
        if pd.notna(row['Variance (Days)']) and row['Variance (Days)'] != 0:
            variance_val = row['Variance (Days)']
            variance_text = f"{variance_val:+g}d"
            finish_date = row['Start Date'] + pd.to_timedelta(row['Actual Duration (Days)'], unit='d')
            fig.add_annotation(x=finish_date, y=i, text=variance_text, showarrow=False, xshift=25, font=dict(color="red" if variance_val > 0 else "green"))
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Task Risk Heatmap")
    risk_map = {'Low': 1, 'Medium': 2, 'High': 3}
    df['Risk Score'] = df['Risk Level'].map(risk_map)
    fig = px.density_heatmap(df, x="Lead Team", y="Task ID", z="Risk Score", histfunc="avg", color_continuous_scale="Reds", title="Heatmap of High-Risk Tasks")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("How to Interpret the Heatmap"):
        st.markdown("""
        **What it is:** This heatmap visualizes the concentration of risk within the project plan. Each cell represents a task, and the color intensity indicates its assigned risk level (High, Medium, Low).
        
        **What it tells you:** It immediately draws your attention to the highest-risk activities and which teams are responsible for them. A cluster of dark red cells indicates a high-risk project phase or a team with many critical responsibilities.
        
        **Actionability:** Focus your management and mitigation efforts on the darkest cells. For example, the high-risk "Transfer Process" task owned by Tech Dev should have a detailed mitigation plan and frequent follow-up.
        """)
