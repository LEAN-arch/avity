# pages/B_Financial_Oversight.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import generate_budget_data
from datetime import date # <-- FIX: Added the missing import

st.set_page_config(page_title="Financial Oversight | Avidity", layout="wide")

st.title("💸 Financial Oversight")
st.markdown("### Managing and monitoring CDMO budgets, purchase orders, and fiscal forecasts.")

budget_df = generate_budget_data()
budget_df['YTD Variance ($M)'] = budget_df['YTD Forecast ($M)'] - budget_df['YTD Actuals ($M)']

st.header("Total Program Financial Health")
total_budget = budget_df['Annual Budget ($M)'].sum()
total_actuals = budget_df['YTD Actuals ($M)'].sum()
total_forecast = budget_df['YTD Forecast ($M)'].sum()
# This line will now work correctly
burn_rate = total_actuals / (date.today().month / 12) if date.today().month > 0 else 0 

fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
fin_col1.metric("Total Annual Budget", f"${total_budget:.1f}M")
fin_col2.metric("YTD Actuals", f"${total_actuals:.1f}M")
fin_col3.metric("Projected Annual Burn", f"${burn_rate:.1f}M", help="YTD Actuals extrapolated to a full year.")
fin_col4.metric("Forecasted Y/E Variance", f"${total_budget - total_forecast:.1f}M", help="Expected surplus/deficit at year-end based on current forecasts.")
st.divider()

st.header("Detailed Financial Analysis")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Budget Allocation by Category")
    fig = px.sunburst(
        budget_df, path=['Category', 'Sub-Category', 'Program'], values='Annual Budget ($M)',
        color='Annual Budget ($M)', color_continuous_scale='Blues',
        title="Annual Budget Allocation ($M)"
    )
    fig.update_layout(height=450, margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("How to Interpret the Sunburst Chart"):
        st.markdown("""
        **What it is:** A hierarchical view of your budget. Each ring represents a different level of the hierarchy.
        - **Center Ring:** High-level budget categories (e.g., External Manufacturing).
        - **Middle Ring:** Sub-categories (e.g., Drug Substance).
        - **Outer Ring:** The specific programs the budget is allocated to.
        
        **Actionability:** Use this to quickly understand the major cost drivers in your budget. A large segment in the outer ring represents a significant investment area.
        """)

with col2:
    st.subheader("YTD Actuals vs. Forecast")
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Actuals', x=budget_df['CDMO'], y=budget_df['YTD Actuals ($M)'], marker_color='#003F87'))
    fig.add_trace(go.Bar(name='Forecast', x=budget_df['CDMO'], y=budget_df['YTD Forecast ($M)'], marker_color='#00AEEF'))
    fig.update_layout(barmode='group', title="YTD Actuals vs. Forecast by Partner", yaxis_title="Amount ($M)", height=450, margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("How to Interpret the Forecast Chart"):
        st.markdown("""
        **What it is:** This chart compares what you have actually spent (Actuals) versus what you *planned* to have spent by this point in the year (Forecast).
        
        **What it tells you:**
        - **Actual > Forecast:** You are spending faster than planned. This could be due to accelerated activities or cost overruns.
        - **Actual < Forecast:** You are spending slower than planned. This could indicate project delays or cost savings.
        
        **Actionability:** Investigate any significant variances to understand the root cause and adjust future financial plans accordingly.
        """)
