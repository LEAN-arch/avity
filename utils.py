# pages/A_CDMO_Drilldown.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import generate_cdmo_data, generate_master_schedule, generate_spc_data, generate_quality_data, generate_risk_register
from datetime import date

st.set_page_config(page_title="CDMO Drilldown | Avidity", layout="wide")

# --- Data Loading ---
cdmo_df = generate_cdmo_data()
schedule_df = generate_master_schedule()
quality_df = generate_quality_data()
risk_df = generate_risk_register()

st.sidebar.title("CDMO Selection")
selected_cdmo = st.sidebar.selectbox("Select a CDMO to view details", cdmo_df['CDMO Name'])

st.title(f"Technical Drilldown: {selected_cdmo}")
cdmo_details = cdmo_df[cdmo_df['CDMO Name'] == selected_cdmo].iloc[0]
st.markdown(f"**Location:** {cdmo_details['Location']} | **Expertise:** {cdmo_details['Expertise']}")
st.divider()

cdmo_schedule = schedule_df[schedule_df['CDMO'] == selected_cdmo]
cdmo_risks = risk_df[risk_df['CDMO'].isin([selected_cdmo, 'All'])]
cdmo_quality = quality_df[quality_df['CDMO'] == selected_cdmo]

tab1, tab2, tab3, tab4 = st.tabs(["🔬 Batch Deep Dive", "📈 Process Capability", "📋 Quality Systems", "🛡️ Continuity & Mitigation"])

with tab1:
    st.header("Batch Deep Dive Analysis")
    st.caption("Perform a detailed analysis of any specific manufacturing batch, including its SPC data and final disposition.")
    selected_batch = st.selectbox("Select a Batch ID for detailed analysis", cdmo_schedule['Batch ID'])
    
    if selected_batch:
        batch_details = cdmo_schedule[cdmo_schedule['Batch ID'] == selected_batch].iloc[0]
        spc_data = generate_spc_data(selected_batch)

        status = batch_details['Status']
        if status == 'Failed':
            st.error(f"**Batch Disposition: FAILED** | Deviation: {batch_details['Deviation ID']}")
        elif status == 'At Risk':
            st.warning(f"**Batch Disposition: AT RISK** | Deviation: {batch_details['Deviation ID']}")
        else:
            st.success("**Batch Disposition: PASSED**")
        st.divider()

        st.subheader(f"Statistical Process Control (SPC) for: {selected_batch}")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=spc_data['Measurement'], y=spc_data['Value'], mode='lines+markers', name='Value', line=dict(color='#003F87')))
        fig.add_trace(go.Scatter(x=spc_data['Measurement'], y=spc_data['Mean'], mode='lines', name='Mean', line=dict(color='green', dash='dash')))
        fig.add_trace(go.Scatter(x=spc_data['Measurement'], y=spc_data['UCL'], mode='lines', name='Control Limit', line=dict(color='orange', dash='dash')))
        fig.add_trace(go.Scatter(x=spc_data['Measurement'], y=spc_data['LCL'], mode='lines', showlegend=False, line=dict(color='orange', dash='dash')))
        fig.add_trace(go.Scatter(x=spc_data['Measurement'], y=spc_data['USL'], mode='lines', name='Spec Limit', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=spc_data['Measurement'], y=spc_data['LSL'], mode='lines', showlegend=False, line=dict(color='red')))
        
        oos = spc_data[(spc_data['Value'] > spc_data['USL']) | (spc_data['Value'] < spc_data['LSL'])]
        if not oos.empty:
            fig.add_trace(go.Scatter(x=oos['Measurement'], y=oos['Value'], mode='markers', marker=dict(color='red', size=12, symbol='x'), name='Out of Spec'))
        
        fig.update_layout(title_text="Control Chart for Oligo Concentration", yaxis_title="Concentration (mg/mL)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Methodology & Actionability: SPC Chart"):
            st.markdown("""
            **Methodology:** Statistical Process Control (SPC) distinguishes between inherent "common cause" variation and unexpected "special cause" variation. This chart plots a Critical Process Parameter (CPP) over time for a single batch.

            **The Math:**
            - **Spec Limits (USL/LSL - Red Lines):** Pre-defined quality requirements (the "Voice of the Customer"). They are not calculated from this data.
            - **Control Limits (UCL/LCL - Orange Dashed Lines):** The "Voice of the Process," calculated as `Mean ± 3 * Standard_Deviation`. A point outside these limits is statistically rare (p < 0.003).

            **Significance & Insights:**
            - **Point outside Spec Limits:** The batch has **failed** to meet a critical quality requirement.
            - **Point outside Control Limits:** The process is **unstable**. An unexpected event occurred, requiring investigation even if the batch is still in spec.
            - **Non-random Patterns (e.g., 7 points trending down):** The process is **drifting out of control**, a leading indicator of future failure.

            **Managerial Actionability:**
            - **Action:** A point out-of-spec triggers a formal **Deviation**.
            - **Action:** A point out-of-control requires a **technical deep-dive** with the CDMO to identify the "special cause" and prevent recurrence.
            """)

with tab2:
    st.header("Process Capability & Performance")
    st.caption("Evaluate long-term process stability and capability across multiple batches.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cycle Time Performance (XmR Chart)")
        completed_batches = cdmo_schedule.dropna(subset=['Actual Cycle Time (Days)'])
        if not completed_batches.empty and len(completed_batches) > 1:
            mean_ct = completed_batches['Actual Cycle Time (Days)'].mean()
            mr = completed_batches['Actual Cycle Time (Days)'].diff().abs()
            ucl = mean_ct + 2.66 * mr.mean()
            lcl = mean_ct - 2.66 * mr.mean()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=completed_batches['Batch ID'], y=completed_batches['Actual Cycle Time (Days)'], mode='lines+markers', name='Cycle Time'))
            fig.add_hline(y=mean_ct, line_dash="dash", line_color="green", annotation_text=f"Mean: {mean_ct:.1f}d")
            fig.add_hline(y=ucl, line_dash="dash", line_color="red", annotation_text="UCL")
            fig.add_hline(y=lcl, line_dash="dash", line_color="red", annotation_text="LCL")
            fig.update_layout(height=400, title="Process Stability: Batch Cycle Times", yaxis_title="Days", margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("At least two completed batches are needed to calculate control limits.")

    with col2:
        st.subheader("Process Capability (Cpk)")
        cpk_data = {'Parameter': ['Oligo Concentration', 'pH', 'Antibody Titer', 'Conjugation Efficiency'],'Cpk Value': [1.45, 1.82, 0.95, 1.10]}
        cpk_df = pd.DataFrame(cpk_data)
        fig = px.bar(cpk_df, x='Cpk Value', y='Parameter', orientation='h', title='Process Capability for Critical Parameters', text='Cpk Value')
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.add_vline(x=1.33, line_dash="dash", line_color="green", annotation_text="Target Cpk")
        fig.add_vline(x=1.0, line_dash="dash", line_color="red", annotation_text="Incapable")
        st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("Methodology & Actionability: Cpk & XmR Charts"):
        st.markdown("""
        **Methodology:**
        - **XmR Chart:** An SPC chart for tracking process stability *between* batches.
        - **Cpk (Process Capability Index):** A standard industry metric that quantifies how well a stable process can meet its specification limits.

        **The Math:**
        - **Cpk = min( (USL - μ) / 3σ , (μ - LSL) / 3σ )**. It measures how many "sigmas" (`σ`) fit between your process mean (`μ`) and the nearest specification limit (USL/LSL).

        **Significance & Insights:**
        - **Cpk < 1.0:** The process is **not capable** and is guaranteed to produce defects. This is a major problem.
        - **1.0 ≤ Cpk < 1.33:** The process is **marginally capable** and requires tight control.
        - **Cpk ≥ 1.33:** The process is considered **capable** and robust. This is the common industry target.

        **Managerial Actionability:**
        - **Action:** Any parameter with a Cpk below 1.33 is a prime candidate for a **continuous improvement project** (tracked on the OpEx page).
        - **Action:** Use this data to justify allocating resources from Technical Development to improve a specific, incapable process step.
        """)

with tab3:
    st.header("Quality Systems Tracker")
    st.caption(f"Open deviations, CAPAs, and change requests for {selected_cdmo}. Prioritize by age and priority.")
    if not cdmo_quality.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Open Records by Type")
            q_counts = cdmo_quality['Type'].value_counts()
            fig = px.bar(q_counts, x=q_counts.index, y=q_counts.values, title="Count of Open Quality Records", labels={'x':'Record Type', 'y':'Count'})
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Record Aging")
            fig = px.bar(cdmo_quality, x='Record ID', y='Days Open', color='Priority', title="Aging of Open Records", color_discrete_map={'Critical':'maroon', 'High':'red', 'Medium':'orange', 'Low':'grey'})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No open quality records for this CDMO.")
            
    with st.expander("View/Edit Detailed Quality Log"):
        if not cdmo_quality.empty:
            st.data_editor(cdmo_quality, use_container_width=True, hide_index=True)

with tab4:
    st.header("Business Continuity & Risk Mitigation")
    st.subheader("Business Continuity Plan (BCP)")
    bcp_status = cdmo_details['BCP Status']
    bcp_last_reviewed = cdmo_details['BCP Last Reviewed']
    bcp_col1, bcp_col2 = st.columns(2)
    bcp_col1.metric("BCP Status", bcp_status)
    if pd.notna(bcp_last_reviewed):
        bcp_col2.metric("BCP Last Reviewed", bcp_last_reviewed.strftime('%Y-%m-%d'))
        if (date.today() - bcp_last_reviewed).days > 365:
            st.warning("BCP review is overdue. Schedule a review with the CDMO.")
    else:
        bcp_col2.metric("BCP Last Reviewed", "N/A")
    st.divider()

    st.subheader("Interactive Risk Mitigation Register")
    st.caption("This register tracks all identified risks and their corresponding mitigation plans. Use it to drive risk reduction activities with the VPT.")
    if cdmo_risks.empty:
        st.success(f"No specific risks currently logged for {selected_cdmo}.")
    else:
        st.data_editor(cdmo_risks, column_config={"Mitigation Status": st.column_config.SelectboxColumn("Status", options=['Planned', 'In Progress', 'Complete', 'On Hold'], required=True), "Risk Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=25, format="%d")}, use_container_width=True, hide_index=True)
