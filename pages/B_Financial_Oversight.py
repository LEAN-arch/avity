# pages/B_Financial_Oversight.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import generate_budget_data

st.set_page_config(page_title="Financial Oversight | Avidity", layout="wide")

st.title("💸 Financial Oversight")
st.markdown("### Managing and monitoring CDMO budgets, purchase orders, and fiscal forecasts.")

# --- Data Loading ---
budget_df = generate_budget_data()

# --- High-Level Financial Summary ---
st.header("Total Program Budget Status")
total_budget = budget_df['Annual Budget ($M)'].sum()
total_actuals = budget_df['Actuals YTD ($M)'].sum()
percent_spent = (total_actuals / total_budget) * 100

fin_col1, fin_col2, fin_col3 = st.columns(3)
fin_col1.metric("Total Annual Budget", f"${total_budget:.1f}M")
fin_col2.metric("Actuals YTD", f"${total_actuals:.1f}M")
fin_col3.metric("Percent of Budget Spent", f"{percent_spent:.1f}%")
st.divider()

# --- Visualizations ---
st.header("Hierarchical Budget Analysis")
col_sunburst, col_table = st.columns([2, 1])

with col_sunburst:
    st.caption("Hierarchical view of the annual budget, from total program down to individual CDMOs and programs.")
    fig = px.sunburst(
        budget_df,
        path=['Budget Type', 'CDMO', 'Program'],
        values='Annual Budget ($M)',
        color='Annual Budget ($M)',
        color_continuous_scale='Blues',
        title="Annual Budget Allocation ($M)"
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with col_table:
    st.caption("Detailed breakdown of budget and actuals.")
    budget_df['% Spent'] = (budget_df['Actuals YTD ($M)'] / budget_df['Annual Budget ($M)']) * 100
    st.dataframe(
        budget_df, use_container_width=True, hide_index=True,
        column_config={
            "Annual Budget ($M)": st.column_config.NumberColumn(format="$%.1fM"),
            "Actuals YTD ($M)": st.column_config.NumberColumn(format="$%.1fM"),
            "% Spent": st.column_config.ProgressColumn(
                "%", min_value=0, max_value=100, format="%.0f%%"
            )
        }
    )
