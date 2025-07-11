# pages/D_Governance_and_Oversight.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import generate_governance_data
from datetime import date

st.set_page_config(page_title="CDMO Governance | Avidity", layout="wide")
st.title("🤝 CDMO Governance & Oversight")
st.markdown("### Tracking the cadence and outcomes of all official partner engagements, including QBRs, audits, and technical meetings.")

gov_df = generate_governance_data()
gov_df['Date'] = pd.to_datetime(gov_df['Date'])

st.header("Governance Program Effectiveness")
total_actions = gov_df['Actions Generated'].sum()
total_closed = gov_df['Actions Closed'].sum()
closure_rate = (total_closed / total_actions) * 100 if total_actions > 0 else 100
avg_days_to_close = 25

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Engagements (YTD)", len(gov_df))
kpi2.metric("Action Item Closure Rate", f"{closure_rate:.1f}%")
kpi3.metric("Avg. Days to Close Action", f"{avg_days_to_close} Days")
st.divider()

st.header("Engagement Analysis")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Action Item Funnel")
    fig = go.Figure(go.Funnel(
        y = ["Engagements", "Actions Generated", "Actions Closed"],
        x = [len(gov_df), total_actions, total_closed],
        textposition = "inside", textinfo = "value+percent previous"
    ))
    fig.update_layout(height=400, title="From Meeting to Action to Closure")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Methodology & Actionability: Action Item Funnel"):
        st.markdown("""
        **Methodology:** A funnel chart visualizes the attrition or conversion rate through sequential stages of a process. Here, it tracks the lifecycle from discussion to action to closure.

        **Significance & Insights:** This chart measures the **effectiveness of the governance process**. A large drop-off between "Actions Generated" and "Actions Closed" is a major red flag, indicating a problem with follow-through and accountability.

        **Managerial Actionability:**
        - **Action:** If the closure rate is low, use this objective data in the next QBR to address the accountability gap with the CDMO. It proves that discussions are not translating into completed work.
        """)

with col2:
    st.subheader("Engagement Cadence")
    gov_df['YearMonth'] = gov_df['Date'].dt.to_period('M').astype(str)
    engagement_counts = gov_df.groupby(['CDMO', 'YearMonth']).size().reset_index(name='counts')
    fig = px.density_heatmap(engagement_counts, x="YearMonth", y="CDMO", z="counts", histfunc="sum", color_continuous_scale="Blues", title="Monthly Engagement Frequency per CDMO")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Methodology & Actionability: Cadence Heatmap"):
        st.markdown("""
        **Methodology:** This heatmap visualizes the frequency of interactions over time.
        **Significance & Insights:** It shows whether a regular cadence of communication is being maintained with each partner, as required by governance plans. Gaps may indicate a relationship or oversight risk.
        **Actionability:**
        - **Action:** Ensure that a consistent schedule of QBRs and technical meetings is maintained for all strategic partners.
        """)

st.header("Official Engagement Log")
st.caption("A detailed, auditable log of all governance meetings.")
st.dataframe(gov_df[['Date', 'CDMO', 'Meeting Type', 'Key Topics', 'Actions Generated', 'Actions Closed']], use_container_width=True, hide_index=True)
