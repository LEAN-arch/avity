# pages/D_Governance_and_Oversight.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import generate_governance_data

st.set_page_config(page_title="CDMO Governance | Avidity", layout="wide")

st.title("🤝 CDMO Governance & Oversight")
st.markdown("### Tracking the cadence and outcomes of all official partner engagements, including QBRs, audits, and technical meetings.")

with st.expander("🌐 Manager's Role: Ensuring Robust Oversight"):
    st.markdown("""
    This dashboard provides a structured and auditable record of our governance program with each CDMO. It ensures we maintain a regular cadence of communication and that key decisions and action items from these meetings are tracked. This is critical for both strong partnerships and demonstrating robust oversight to regulatory authorities.
    """)

# --- Data Loading ---
gov_df = generate_governance_data()
gov_df['Date'] = pd.to_datetime(gov_df['Date'])

# --- Engagement Cadence Heatmap ---
st.header("Engagement Cadence")
st.caption("Heatmap showing the frequency and type of interactions with each CDMO partner over time.")
gov_df['YearMonth'] = gov_df['Date'].dt.to_period('M').astype(str)
engagement_counts = gov_df.groupby(['CDMO', 'YearMonth']).size().reset_index(name='counts')

fig = px.density_heatmap(
    engagement_counts,
    x="YearMonth",
    y="CDMO",
    z="counts",
    histfunc="sum",
    color_continuous_scale="Blues",
    title="Monthly Engagement Frequency per CDMO"
)
st.plotly_chart(fig, use_container_width=True)


# --- Governance Log ---
st.header("Official Engagement Log")
st.caption("A detailed, editable log of all governance meetings.")
st.data_editor(
    gov_df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Date": st.column_config.DateColumn("Visit Date", format="YYYY-MM-DD", required=True),
        "Meeting Type": st.column_config.SelectboxColumn("Meeting Type", options=['Quarterly Business Review', 'Person-in-Plant', 'Audit', 'VPT Meeting'], required=True),
        "Key Topics": st.column_config.TextColumn("Key Topics", width="large", required=True),
        "Action Items": st.column_config.NumberColumn("# of Action Items", required=True)
    }
)
