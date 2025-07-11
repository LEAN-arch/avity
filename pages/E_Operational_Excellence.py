# pages/E_Operational_Excellence.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import generate_op_ex_data

st.set_page_config(page_title="Operational Excellence | Avidity", layout="wide")

st.title("⚙️ Operational Excellence Portfolio")
st.markdown("### Driving and tracking continuous improvement initiatives to enhance manufacturing efficiency, yield, and compliance.")

# --- Data Loading ---
opex_df = generate_op_ex_data()

# --- KPIs ---
st.header("Program Impact & ROI")
total_projects = len(opex_df)
completed_projects = opex_df[opex_df['Status'] == 'Complete'].shape[0]
potential_annual_savings = opex_df[opex_df['Status'] != 'Complete']['Financial Impact ($K/yr)'].sum()
avg_roi = opex_df['ROI'].mean()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Active Initiatives", total_projects)
kpi2.metric("Completed Initiatives", completed_projects)
kpi3.metric("Potential Annual Savings", f"${potential_annual_savings:,.0f}K")
kpi4.metric("Average Project ROI", f"{avg_roi:.1f}x")
st.divider()

# --- Impact vs. Feasibility Matrix ---
st.header("Initiative Prioritization Matrix")
st.caption("Prioritizing projects based on their financial/quality impact and technical feasibility. Bubble size indicates implementation cost.")

fig = px.scatter(
    opex_df,
    x="Technical Feasibility (1-5)",
    y="Financial Impact ($K/yr)",
    size="Implementation Cost ($K)",
    color="Status",
    hover_name="Title",
    text="Project ID",
    size_max=60,
    color_discrete_map={
        'In Progress': '#00AEEF',
        'Complete': '#003F87',
        'Planned': 'grey'
    }
)
# Add quadrants for strategic categorization
fig.add_vline(x=3.5, line_dash="dash")
fig.add_hline(y=opex_df["Financial Impact ($K/yr)"].median(), line_dash="dash")

fig.add_annotation(x=4.5, y=opex_df["Financial Impact ($K/yr)"].max(), text="<b>Quick Wins</b>", showarrow=False, font_color="green")
fig.add_annotation(x=2, y=opex_df["Financial Impact ($K/yr)"].max(), text="<b>Major Projects</b>", showarrow=False, font_color="blue")
fig.add_annotation(x=4.5, y=opex_df["Financial Impact ($K/yr)"].min(), text="<b>Fill-Ins</b>", showarrow=False, font_color="orange")
fig.add_annotation(x=2, y=opex_df["Financial Impact ($K/yr)"].min(), text="<b>Re-evaluate</b>", showarrow=False, font_color="red")

fig.update_traces(textposition='top center')
fig.update_layout(height=600, title="OpEx Project Portfolio")
st.plotly_chart(fig, use_container_width=True)
st.divider()

# --- Detailed Project Tracker ---
st.header("Detailed Initiative Tracker")
st.caption("A granular list of all continuous improvement projects.")
st.dataframe(
    opex_df,
    use_container_width=True, hide_index=True,
    column_config={
        "ROI": st.column_config.NumberColumn("ROI", format="%.1fx"),
        "Financial Impact ($K/yr)": st.column_config.NumberColumn(format="$%dK"),
        "Implementation Cost ($K)": st.column_config.NumberColumn(format="$%dK")
    }
)
