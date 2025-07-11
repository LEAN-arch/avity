# pages/B_Financial_Oversight.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import generate_budget_data, generate_master_schedule
from datetime import date

st.set_page_config(page_title="Financial Oversight | Avidity", layout="wide")
st.title("💸 Financial & Performance Analytics")
st.markdown("### Analyzing spend, forecasting, and operational efficiency across the CDMO network.")

# --- Data Loading and Prep ---
budget_df = generate_budget_data()
schedule_df = generate_master_schedule()
today = date.today()
time_elapsed_pct = (today.month -1) / 12 + today.day / (30*12) # Approximate % of year elapsed

# --- Strategic Financial KPIs ---
st.header("Portfolio Financial Health")
total_budget = budget_df['Annual Budget ($M)'].sum()
total_actuals = budget_df['YTD Actuals ($M)'].sum()
total_eac = budget_df['Estimate at Completion ($M)'].sum()
spend_rate_pct = (total_actuals / total_budget) * 100
avg_cost_per_batch = schedule_df['Cost per Batch ($K)'].mean()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Annual Budget", f"${total_budget:.1f}M")
kpi2.metric(f"Spend Rate ({spend_rate_pct:.0%}) vs. Time Elapsed ({time_elapsed_pct:.0%})", f"${total_actuals:.1f}M")
kpi3.metric("Estimate at Completion (EAC)", f"${total_eac:.1f}M", delta=f"${total_eac - total_budget:.1f}M vs Budget", delta_color="inverse")
kpi4.metric("Average Cost per Batch", f"${avg_cost_per_batch:.0f}K")
st.divider()

# --- Visualization Overhaul ---
st.header("Financial Performance Visualizations")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Forecasted Year-End Variance (Waterfall)")
    remaining_forecast = budget_df['Remaining Forecast ($M)'].sum()
    ytd_actuals = budget_df['YTD Actuals ($M)'].sum()
    year_end_variance = total_budget - total_eac
    
    fig_waterfall = go.Figure(go.Waterfall(
        orientation="v", measure=["absolute", "relative", "relative", "total"],
        x=["Annual Budget", "YTD Actuals", "Remaining Forecast", "Projected Year-End Variance"],
        text=[f"${total_budget:.1f}M", f"-${ytd_actuals:.1f}M", f"-${remaining_forecast:.1f}M", f"${year_end_variance:.1f}M"],
        y=[total_budget, -ytd_actuals, -remaining_forecast, year_end_variance],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#F37021"}},
        totals={"marker": {"color": "#003F87" if year_end_variance >= 0 else "#DA291C"}}
    ))
    fig_waterfall.update_layout(title="Projected Year-End Financial Position", yaxis_title="Amount ($M)", height=450)
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    with st.expander("Methodology: Variance Waterfall"):
        st.markdown("This chart shows how the budget is consumed to project the final year-end variance. It starts with the total budget, subtracts money already spent (Actuals), then subtracts money forecasted to be spent, arriving at the final projected surplus or deficit. **Action:** A projected deficit (red total) requires immediate action, such as deferring projects or seeking additional funding.")

with col2:
    st.subheader("Quarterly Spend vs. Plan")
    q_data = budget_df.melt(
        id_vars=['CDMO'], 
        value_vars=['Q1 Actuals ($M)', 'Q2 Actuals ($M)', 'Q3 Plan ($M)', 'Q4 Plan ($M)'],
        var_name='Quarter', value_name='Amount ($M)'
    )
    q_data['Type'] = q_data['Quarter'].apply(lambda x: 'Actual' if 'Actuals' in x else 'Plan')
    q_data['Quarter'] = q_data['Quarter'].str.extract(r'(Q\d)')
    
    fig_q = px.bar(q_data, x='Quarter', y='Amount ($M)', color='Type', barmode='group', title="Quarterly Spend Cadence", color_discrete_map={'Actual':'#003F87', 'Plan':'#BDBDBD'})
    fig_q.update_layout(height=450, yaxis_title="Amount ($M)")
    st.plotly_chart(fig_q, use_container_width=True)

    with st.expander("Methodology: Spend Cadence"):
        st.markdown("This chart compares the planned spending cadence against actuals for each quarter. **Action:** Significant deviations from the plan (e.g., spending much more in Q2 than planned) can signal accelerated projects or cost overruns, while spending less can signal delays. This helps refine the accuracy of future financial forecasting.")

st.subheader("Cost Efficiency Analysis")
cost_df = schedule_df[schedule_df['Status'].isin(['Shipped', 'Awaiting Release', 'Failed'])].copy()
cost_df['Finish Date'] = pd.to_datetime(cost_df['End Date'])
fig_cost = px.scatter(
    cost_df, x='Finish Date', y='Cost per Batch ($K)', color='Program', size='Yield (%)',
    title="Cost Per Batch vs. Yield Over Time", trendline="ols", trendline_scope="overall"
)
st.plotly_chart(fig_cost, use_container_width=True)

with st.expander("Methodology: Efficiency Analysis"):
    st.markdown("This chart plots the cost of each completed batch against its final yield. The size of the bubble represents the yield, providing a multi-dimensional view of efficiency. The black dashed line is an Ordinary Least Squares (OLS) trendline showing the overall cost trend. **Action:** A rising trendline indicates decreasing cost efficiency over time, requiring investigation. High-cost, low-yield batches (bottom left) should be analyzed as case studies for process improvement.")
