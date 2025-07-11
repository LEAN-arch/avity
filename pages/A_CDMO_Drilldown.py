# pages/A_CDMO_Drilldown.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import generate_cdmo_data, generate_master_schedule, generate_batch_data, generate_quality_data, generate_risk_register
from datetime import date

st.set_page_config(page_title="CDMO Drilldown | Avidity", layout="wide")

# --- Data Loading ---
cdmo_df = generate_cdmo_data()
schedule_df = generate_master_schedule()
quality_df = generate_quality_data()
risk_df = generate_risk_register()

# --- Sidebar for CDMO Selection ---
st.sidebar.title("CDMO Selection")
selected_cdmo = st.sidebar.selectbox("Select a CDMO to view details", cdmo_df['CDMO Name'])

# --- Header ---
st.title(f"Technical Drilldown: {selected_cdmo}")
cdmo_details = cdmo_df[cdmo_df['CDMO Name'] == selected_cdmo].iloc[0]
st.markdown(f"**Location:** {cdmo_details['Location']} | **Expertise:** {cdmo_details['Expertise']}")
st.divider()

# Filter data for the selected CDMO
cdmo_schedule = schedule_df[schedule_df['CDMO'] == selected_cdmo]
cdmo_risks = risk_df[risk_df['CDMO'].isin([selected_cdmo, 'All'])]
cdmo_quality = quality_df[quality_df['CDMO'] == selected_cdmo]

# --- Tabbed Layout ---
tab1, tab2, tab3, tab5 = st.tabs(["📈 Operational Performance", "🔬 Batch Deep Dive", "📋 Quality & Compliance", "🛡️ Continuity & Mitigation"])

# (Tabs 1, 2, and 3 are unchanged)
with tab1:
    st.header("Operational Performance Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Production Funnel")
        funnel_data = cdmo_schedule['Status'].value_counts().reindex(['Planned', 'In Production', 'Awaiting Release', 'Shipped']).fillna(0)
        fig = go.Figure(go.Funnel(y=funnel_data.index, x=funnel_data.values, textinfo="value+percent initial"))
        fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Cycle Time Performance (XmR Chart)")
        completed_batches = cdmo_schedule.dropna(subset=['Actual Cycle Time (Days)'])
        if not completed_batches.empty:
            mean_ct = completed_batches['Actual Cycle Time (Days)'].mean()
            ucl = mean_ct + 2.66 * completed_batches['Actual Cycle Time (Days)'].diff().abs().mean()
            lcl = mean_ct - 2.66 * completed_batches['Actual Cycle Time (Days)'].diff().abs().mean()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=completed_batches['Batch ID'], y=completed_batches['Actual Cycle Time (Days)'], mode='lines+markers', name='Cycle Time'))
            fig.add_hline(y=mean_ct, line_dash="dash", line_color="green", annotation_text="Mean")
            fig.add_hline(y=ucl, line_dash="dash", line_color="red", annotation_text="UCL")
            fig.add_hline(y=lcl, line_dash="dash", line_color="red", annotation_text="LCL")
            fig.update_layout(height=400, title="Process Stability: Batch Cycle Times", yaxis_title="Days", margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No completed batches with cycle time data for this CDMO yet.")

with tab2:
    st.header("Batch Deep Dive Analysis")
    selected_batch = st.selectbox("Select a Batch ID for detailed analysis", cdmo_schedule['Batch ID'])
    if selected_batch:
        ipc_data, analytical_data = generate_batch_data(selected_batch)
        st.subheader(f"In-Process Control (SPC) for: {selected_batch}")
        param = st.radio("Select Parameter to Plot", ipc_data['Parameter'].unique(), horizontal=True)
        param_data = ipc_data[ipc_data['Parameter'] == param]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=param_data['Step'], y=param_data['Value'], mode='lines+markers', name='Value'))
        fig.add_hline(y=param_data['USL'].iloc[0], line_dash="solid", line_color="red", annotation_text="USL")
        fig.add_hline(y=param_data['LSL'].iloc[0], line_dash="solid", line_color="red", annotation_text="LSL")
        oos = param_data[(param_data['Value'] > param_data['USL']) | (param_data['Value'] < param_data['LSL'])]
        if not oos.empty:
            fig.add_trace(go.Scatter(x=oos['Step'], y=oos['Value'], mode='markers', marker=dict(color='red', size=12, symbol='x'), name='Out of Spec'))
        fig.update_layout(title=f"SPC Chart for {param}", yaxis_title=param)
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Final Analytical Results")
        st.dataframe(analytical_data, use_container_width=True, hide_index=True)

with tab3:
    st.header("Quality & Compliance Tracker")
    st.caption(f"Open deviations, CAPAs, and change requests for {selected_cdmo}.")
    if cdmo_quality.empty:
        st.success(f"No open quality records for {selected_cdmo}.")
    else:
        st.data_editor(cdmo_quality, column_config={"Status": st.column_config.SelectboxColumn("Status", options=['Investigation', 'Pending Approval', 'Effectiveness Check', 'Closed'], required=True), "Owner": st.column_config.SelectboxColumn("Owner", options=['Manager', 'QA', 'Tech Dev', 'Supply Chain'], required=True)}, use_container_width=True, hide_index=True)

# NEW: Continuity & Mitigation Tab
with tab5:
    st.header("Business Continuity & Risk Mitigation")
    
    # --- Business Continuity Plan Section ---
    st.subheader("Business Continuity Plan (BCP)")
    bcp_status = cdmo_details['BCP Status']
    bcp_last_reviewed = cdmo_details['BCP Last Reviewed']
    
    bcp_col1, bcp_col2 = st.columns(2)
    bcp_col1.metric("BCP Status", bcp_status)
    if pd.notna(bcp_last_reviewed):
        bcp_col2.metric("BCP Last Reviewed", bcp_last_reviewed.strftime('%Y-%m-%d'))
        # Flag if review is more than a year old
        if (date.today() - bcp_last_reviewed).days > 365:
            st.warning("BCP review is overdue. Schedule a review with the CDMO.")
    else:
        bcp_col2.metric("BCP Last Reviewed", "N/A")

    st.info("This section tracks the formal BCP. Ensure plans are reviewed annually and cover key scenarios like natural disasters, geopolitical events, or critical equipment failure.")
    st.divider()

    # --- Interactive Risk Mitigation Tracker ---
    st.subheader("Interactive Risk Mitigation Register")
    st.caption("Track and update mitigation strategies for all identified risks. This serves as the action plan for risk reduction.")

    if cdmo_risks.empty:
        st.success(f"No specific risks currently logged for {selected_cdmo}.")
    else:
        st.data_editor(
            cdmo_risks,
            column_config={
                "Description": st.column_config.TextColumn(width="large"),
                "Mitigation Strategy": st.column_config.TextColumn(width="large", required=True),
                "Mitigation Status": st.column_config.SelectboxColumn(
                    "Status", 
                    options=['Planned', 'In Progress', 'Complete', 'On Hold'], 
                    required=True
                ),
                "Risk Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=25, format="%d")
            },
            use_container_width=True, hide_index=True
        )
