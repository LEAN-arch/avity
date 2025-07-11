# pages/A_CDMO_Drilldown.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    generate_cdmo_data, generate_master_schedule, generate_spc_data, 
    generate_quality_data, generate_risk_register, generate_cdmo_kpis, generate_cpk_data
)
from datetime import date

st.set_page_config(page_title="CDMO Drilldown | Avidity", layout="wide")

# --- Master Data Loading (once per page load) ---
cdmo_master_df = generate_cdmo_data()
schedule_master_df = generate_master_schedule()
quality_master_df = generate_quality_data()
risk_master_df = generate_risk_register()

# --- Sidebar for CDMO Selection ---
st.sidebar.title("CDMO Selection")
selected_cdmo = st.sidebar.selectbox(
    "Select a CDMO to view details",
    cdmo_master_df['CDMO Name'],
    index=0 # Default to the first CDMO
)

# --- Header ---
st.title(f"Technical Drilldown: {selected_cdmo}")
cdmo_details = cdmo_master_df[cdmo_master_df['CDMO Name'] == selected_cdmo].iloc[0]
st.markdown(f"**Location:** {cdmo_details['Location']} | **Expertise:** {cdmo_details['Expertise']}")
st.divider()

# --- DYNAMIC DATA GENERATION & FILTERING ---
# Filter master dataframes for the selected CDMO
cdmo_schedule = schedule_master_df[schedule_master_df['CDMO'] == selected_cdmo]
cdmo_risks = risk_master_df[risk_master_df['CDMO'].isin([selected_cdmo, 'All'])]
cdmo_quality = quality_master_df[quality_master_df['CDMO'] == selected_cdmo]
# Generate unique, CDMO-specific data using the new utility functions
kpi_df = generate_cdmo_kpis(selected_cdmo)
cpk_df = generate_cpk_data(selected_cdmo)


# --- Tabbed Layout ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Operational Performance", "🔬 Batch Deep Dive", "📋 Quality Systems", "🛡️ Continuity & Mitigation"])

with tab1:
    st.header("Operational Performance Dashboard")
    st.caption("Historical performance trends and long-term process stability for this partner.")
    
    # Historical KPIs
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Latest On-Time Delivery", f"{kpi_df['On-Time Delivery (%)'].iloc[-1]:.1f}%")
    kpi_col2.metric("Latest Deviations per Batch", f"{kpi_df['Deviations per Batch'].iloc[-1]:.2f}")
    kpi_col3.metric("Batches in Production", cdmo_schedule[cdmo_schedule['Status'] == 'In Production'].shape[0])
    st.divider()

    col_hist, col_spc = st.columns(2)
    with col_hist:
        st.subheader("Historical KPI Trends")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=kpi_df['Quarter'], y=kpi_df['On-Time Delivery (%)'], name='On-Time Delivery (%)'))
        fig1.add_trace(go.Scatter(x=kpi_df['Quarter'], y=kpi_df['Deviations per Batch'], name='Devs per Batch', yaxis='y2'))
        fig1.update_layout(
            height=400, title="Quarterly Performance Trends", yaxis=dict(title='On-Time Delivery (%)'),
            yaxis2=dict(title='Deviations per Batch', overlaying='y', side='right'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_spc:
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
            st.info("At least two completed batches are needed to calculate control limits for cycle time.")

with tab2:
    st.header("Batch Deep Dive & Process Capability")
    
    col_batch, col_cpk = st.columns([2,1])
    with col_batch:
        st.subheader("Batch-Specific SPC Analysis")
        if not cdmo_schedule.empty:
            selected_batch = st.selectbox("Select a Batch ID for SPC analysis", cdmo_schedule['Batch ID'])
            if selected_batch:
                spc_data = generate_spc_data(selected_batch)
                fig_spc = go.Figure()
                fig_spc.add_trace(go.Scatter(x=spc_data['Measurement'], y=spc_data['Value'], mode='lines+markers', name='Value', line=dict(color='#003F87')))
                fig_spc.add_trace(go.Scatter(x=spc_data['Measurement'], y=spc_data['UCL'], mode='lines', name='Control Limit', line=dict(color='orange', dash='dash')))
                fig_spc.add_trace(go.Scatter(x=spc_data['Measurement'], y=spc_data['LCL'], mode='lines', showlegend=False, line=dict(color='orange', dash='dash')))
                fig_spc.add_trace(go.Scatter(x=spc_data['Measurement'], y=spc_data['USL'], mode='lines', name='Spec Limit', line=dict(color='red')))
                fig_spc.add_trace(go.Scatter(x=spc_data['Measurement'], y=spc_data['LSL'], mode='lines', showlegend=False, line=dict(color='red')))
                oos = spc_data[(spc_data['Value'] > spc_data['USL']) | (spc_data['Value'] < spc_data['LSL'])]
                if not oos.empty:
                    fig_spc.add_trace(go.Scatter(x=oos['Measurement'], y=oos['Value'], mode='markers', marker=dict(color='red', size=12, symbol='x'), name='Out of Spec'))
                fig_spc.update_layout(height=400, title_text=f"Control Chart for {selected_batch}", yaxis_title="Value", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig_spc, use_container_width=True)
        else:
            st.info("No batches scheduled for this CDMO.")
    
    with col_cpk:
        st.subheader("Process Capability (Cpk)")
        st.info("Cpk > 1.33 is capable. Cpk < 1.0 is not capable.")
        fig_cpk = px.bar(cpk_df, x='Cpk Value', y='Parameter', orientation='h', title='Process Capability', text='Cpk Value')
        fig_cpk.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_cpk.add_vline(x=1.33, line_dash="dash", line_color="green", annotation_text="Target")
        fig_cpk.add_vline(x=1.0, line_dash="dash", line_color="red")
        fig_cpk.update_layout(height=400, yaxis_title=None, margin=dict(t=40, b=20))
        st.plotly_chart(fig_cpk, use_container_width=True)


with tab3:
    st.header("Quality Systems Tracker")
    st.caption(f"Open deviations, CAPAs, and change requests for {selected_cdmo}. Prioritize by age and priority.")
    if not cdmo_quality.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Open Records by Type")
            q_counts = cdmo_quality['Type'].value_counts()
            fig = px.pie(q_counts, names=q_counts.index, values=q_counts.values, title="Distribution of Open Records", hole=0.3)
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
