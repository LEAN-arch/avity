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
selected_cdmo = st.sidebar.selectbox("Select a CDMO to view details", cdmo_master_df['CDMO Name'], index=0)

# --- Header ---
st.title(f"Technical Drilldown: {selected_cdmo}")
cdmo_details = cdmo_master_df[cdmo_master_df['CDMO Name'] == selected_cdmo].iloc[0]
st.markdown(f"**Location:** {cdmo_details['Location']} | **Expertise:** {cdmo_details['Expertise']}")
st.divider()

# --- DYNAMIC DATA GENERATION & FILTERING ---
cdmo_schedule = schedule_master_df[schedule_master_df['CDMO'] == selected_cdmo]
cdmo_risks = risk_master_df[risk_master_df['CDMO'].isin([selected_cdmo, 'All'])]
cdmo_quality = quality_master_df[quality_master_df['CDMO'] == selected_cdmo]
kpi_df = generate_cdmo_kpis(selected_cdmo)
cpk_df = generate_cpk_data(selected_cdmo)

# --- Tabbed Layout ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Operational Performance", "🔬 Batch Deep Dive", "📋 Quality Systems", "🛡️ Continuity & Mitigation"])

with tab1:
    # This tab remains the same as it was already highly technical
    st.header("Operational Performance Dashboard") # ... content ...
    st.caption("Historical performance trends and long-term process stability for this partner.")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Latest On-Time Delivery", f"{kpi_df['On-Time Delivery (%)'].iloc[-1]:.1f}%")
    kpi_col2.metric("Latest Deviations per Batch", f"{kpi_df['Deviations per Batch'].iloc[-1]:.2f}")
    kpi_col3.metric("Batches in Production", cdmo_schedule[cdmo_schedule['Status'] == 'In Production'].shape[0])
    st.divider()
    col_hist, col_spc = st.columns(2)
    with col_hist: # ... content ...
        st.subheader("Historical KPI Trends")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=kpi_df['Quarter'], y=kpi_df['On-Time Delivery (%)'], name='On-Time Delivery (%)'))
        fig1.add_trace(go.Scatter(x=kpi_df['Quarter'], y=kpi_df['Deviations per Batch'], name='Devs per Batch', yaxis='y2'))
        fig1.update_layout(height=400, title="Quarterly Performance Trends", yaxis=dict(title='On-Time Delivery (%)'), yaxis2=dict(title='Deviations per Batch', overlaying='y', side='right'), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig1, use_container_width=True)
    with col_spc: # ... content ...
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
    # This tab also remains the same
    st.header("Batch Deep Dive & Process Capability") # ... content ...
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
    with col_cpk: # ... content ...
        st.subheader("Process Capability (Cpk)")
        st.info("Cpk > 1.33 is capable. Cpk < 1.0 is not capable.")
        fig_cpk = px.bar(cpk_df, x='Cpk Value', y='Parameter', orientation='h', title='Process Capability', text='Cpk Value')
        fig_cpk.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_cpk.add_vline(x=1.33, line_dash="dash", line_color="green", annotation_text="Target")
        fig_cpk.add_vline(x=1.0, line_dash="dash", line_color="red")
        fig_cpk.update_layout(height=400, yaxis_title=None, margin=dict(t=40, b=20))
        st.plotly_chart(fig_cpk, use_container_width=True)

# --- START: Overhauled Quality Systems Tab ---
with tab3:
    st.header(f"Quality Systems Analysis for {selected_cdmo}")
    st.caption("Analyze quality event trends, root causes, and closure effectiveness.")

    if cdmo_quality.empty:
        st.success("No open quality records for this CDMO.")
    else:
        # --- KPIs for Quality ---
        q_kpi1, q_kpi2, q_kpi3 = st.columns(3)
        open_records = cdmo_quality[cdmo_quality['Status'] != 'Closed']
        q_kpi1.metric("Open Quality Records", len(open_records))
        q_kpi2.metric("Avg. Days Open", f"{open_records['Days Open'].mean():.1f}")
        critical_high = open_records[open_records['Priority'].isin(['Critical', 'High'])]
        q_kpi3.metric("Open Critical/High Priority", len(critical_high), delta_color="inverse")
        st.divider()

        q_col1, q_col2 = st.columns(2)
        with q_col1:
            st.subheader("Deviation Root Cause Analysis (Pareto)")
            deviation_df = cdmo_quality[cdmo_quality['Type'] == 'Deviation'].dropna(subset=['Root Cause Category'])
            if not deviation_df.empty:
                pareto_data = deviation_df['Root Cause Category'].value_counts().reset_index()
                pareto_data.columns = ['Category', 'Count']
                pareto_data = pareto_data.sort_values(by='Count', ascending=False)
                pareto_data['Cumulative %'] = (pareto_data['Count'].cumsum() / pareto_data['Count'].sum()) * 100
                
                fig_pareto = go.Figure()
                fig_pareto.add_trace(go.Bar(x=pareto_data['Category'], y=pareto_data['Count'], name='Count', marker_color='#003F87'))
                fig_pareto.add_trace(go.Scatter(x=pareto_data['Category'], y=pareto_data['Cumulative %'], name='Cumulative %', yaxis='y2', line=dict(color='#F37021')))
                fig_pareto.update_layout(height=400, title_text="Pareto Chart of Deviation Root Causes", yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0, 101]))
                st.plotly_chart(fig_pareto, use_container_width=True)
            else:
                st.info("No deviations with root cause data available.")
                
            with st.expander("Methodology: Pareto Analysis"):
                st.markdown("A Pareto chart follows the 80/20 rule, showing that roughly 80% of problems ('Count') come from 20% of causes ('Category'). **Action:** Focus your continuous improvement efforts on the top 1-2 root causes to achieve the greatest impact on reducing deviations.")

        with q_col2:
            st.subheader("Monthly Quality Event Trend")
            trend_data = cdmo_quality.copy()
            trend_data['Month'] = pd.to_datetime(trend_data['Open Date']).dt.to_period('M').astype(str)
            
            fig_trend = px.histogram(trend_data, x='Month', color='Type', title="Quality Records Opened Over Time", barmode='stack')
            fig_trend.update_layout(height=400)
            st.plotly_chart(fig_trend, use_container_width=True)

            with st.expander("Methodology: Trend Analysis"):
                st.markdown("This chart tracks the number and type of new quality records opened each month. **Action:** A rising trend indicates deteriorating quality performance at the CDMO, while a falling trend shows improvement. Use this to assess the effectiveness of implemented CAPAs and improvement initiatives.")

    with st.expander("View/Edit Detailed Quality Log"):
        st.data_editor(cdmo_quality, use_container_width=True, hide_index=True)
# --- END: Overhauled Quality Systems Tab ---

with tab4:
    # This tab remains the same as it was already well-structured
    st.header("Business Continuity & Risk Mitigation") # ... content ...
    st.subheader("Business Continuity Plan (BCP)")
    bcp_status = cdmo_details['BCP Status']; bcp_last_reviewed = cdmo_details['BCP Last Reviewed']
    bcp_col1, bcp_col2 = st.columns(2)
    bcp_col1.metric("BCP Status", bcp_status)
    if pd.notna(bcp_last_reviewed):
        bcp_col2.metric("BCP Last Reviewed", bcp_last_reviewed.strftime('%Y-%m-%d'))
        if (date.today() - bcp_last_reviewed).days > 365: st.warning("BCP review is overdue.")
    else:
        bcp_col2.metric("BCP Last Reviewed", "N/A")
    st.divider()
    st.subheader("Interactive Risk Mitigation Register")
    st.caption("This register tracks all identified risks and their corresponding mitigation plans. Use it to drive risk reduction activities with the VPT.")
    if cdmo_risks.empty:
        st.success(f"No specific risks currently logged for {selected_cdmo}.")
    else:
        st.data_editor(cdmo_risks, column_config={"Mitigation Status": st.column_config.SelectboxColumn("Status", options=['Planned', 'In Progress', 'Complete', 'On Hold'], required=True), "Risk Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=25, format="%d")}, use_container_width=True, hide_index=True)
