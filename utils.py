# utils.py
import pandas as pd
import numpy as np
from datetime import date, timedelta

def generate_cdmo_data():
    """Generates a list of mock CDMO partners with performance and BCP metrics."""
    data = {
        'CDMO Name': ['Catalent Pharma', 'WuXi Biologics', 'Lonza Group', 'Fujifilm Diosynth'],
        'Location': ['Bloomington, IN, USA', 'Dundalk, Ireland', 'Visp, Switzerland', 'Hillerød, Denmark'],
        'Status': ['Active', 'Active', 'Onboarding', 'Active'],
        'Expertise': ['Antibody Production', 'Oligonucleotide Synthesis', 'AOC Conjugation & Fill-Finish', 'Antibody Production'],
        'Avg. On-Time Delivery (%)': [98, 85, 99, 92],
        'Avg. Batch Success Rate (%)': [95, 100, 100, 98],
        'Avg. Yield (%)': [82, 88, 85, 84],
        'Batches YTD': [12, 25, 4, 15],
        # NEW: BCP Details
        'BCP Status': ['Approved', 'Under Review', 'Draft', 'Approved'],
        'BCP Last Reviewed': [date(2023, 12, 1), date(2024, 6, 5), None, date(2024, 1, 15)]
    }
    return pd.DataFrame(data)

def generate_master_schedule():
    """Generates a master production schedule with technical details."""
    today = date.today()
    data = {
        'Batch ID': ['AVC-DM1-P3-B005', 'AVC-DM1-P3-B006', 'AVC-DMD-P2-B003', 'AVC-FSHD-P2-B002', 'AVC-DMD-P2-B004'],
        'Product': ['AOC-1001', 'AOC-1001', 'AOC-1021', 'AOC-1044', 'AOC-1021'],
        'Program': ['DM1', 'DM1', 'DMD', 'FSHD', 'DMD'],
        'CDMO': ['WuXi Biologics', 'Catalent Pharma', 'Fujifilm Diosynth', 'WuXi Biologics', 'Lonza Group'],
        'Status': ['In Production', 'At Risk', 'Awaiting Release', 'Shipped', 'Planned'],
        'Start Date': [today - timedelta(days=30), today - timedelta(days=20), today - timedelta(days=60), today - timedelta(days=90), today + timedelta(days=10)],
        'End Date': [today + timedelta(days=60), today + timedelta(days=45), today - timedelta(days=10), today - timedelta(days=30), today + timedelta(days=90)],
        'Planned Cycle Time (Days)': [90, 65, 50, 60, 80],
        'Actual Cycle Time (Days)': [92, 68, 51, 60, np.nan],
        'Yield (%)': [88.1, np.nan, 84.5, 90.2, np.nan],
        'Deviation ID': [None, 'DEV-24-015', None, None, None]
    }
    return pd.DataFrame(data)

def generate_risk_register():
    """Generates an enhanced risk register."""
    data = {
        'Risk ID': ['RSK-SUP-01', 'RSK-TECH-01', 'RSK-COMP-01', 'RSK-GEO-01'],
        'CDMO': ['WuXi Biologics', 'Lonza Group', 'All', 'Catalent Pharma'],
        'Description': ['Single-source for critical raw material faces shipping delays.', 'New conjugation process shows yield variability at scale.', 'Upcoming EMA inspection may scrutinize data integrity of batch records.', 'Geopolitical tensions could impact shipping lanes from US facility.'],
        'Impact': [4, 4, 5, 3], # 1-5 Scale
        'Probability': [3, 4, 2, 2], # 1-5 Scale
        'Owner': ['Supply Chain', 'Tech Dev', 'Quality', 'Manager'],
        # NEW: Mitigation Details
        'Mitigation Strategy': ['Qualify second supplier (Project OpEx-003).', 'Perform DOE to optimize process parameters.', 'Conduct internal audit and data review ahead of inspection.', 'Increase safety stock at domestic warehouse.'],
        'Mitigation Status': ['In Progress', 'Planned', 'In Progress', 'Complete']
    }
    df = pd.DataFrame(data)
    df['Risk Score'] = df['Impact'] * df['Probability']
    return df.sort_values(by='Risk Score', ascending=False)

# NEW: Data for Operational Excellence Page
def generate_op_ex_data():
    """Generates a portfolio of continuous improvement projects."""
    data = {
        'Project ID': ['OpEx-001', 'OpEx-002', 'OpEx-003', 'OpEx-004'],
        'Title': ['Improve Conjugation Yield', 'Reduce Cycle Time for Antibody Prod.', 'Qualify 2nd Supplier for Oligo', 'Automate Deviation Trending'],
        'Lead': ['Tech Dev', 'Manager', 'Supply Chain', 'Quality'],
        'CDMO': ['Lonza Group', 'Catalent Pharma', 'WuXi Biologics', 'All'],
        'Status': ['In Progress', 'Complete', 'In Progress', 'Planned'],
        'Financial Impact ($K/yr)': [500, 250, 1500, 50],
        'Technical Feasibility (1-5)': [3, 5, 4, 5],
        'Implementation Cost ($K)': [75, 20, 300, 40]
    }
    df = pd.DataFrame(data)
    df['ROI'] = df['Financial Impact ($K/yr)'] / df['Implementation Cost ($K)']
    return df

# (All other utility functions remain the same)
def generate_batch_data(batch_id):
    np.random.seed(hash(batch_id) % (2**32 - 1))
    ipc_data = pd.DataFrame({'Step': [f'IPC-{i+1}' for i in range(10)],'Parameter': ['pH'] * 5 + ['Temperature'] * 5,'Value': np.concatenate([np.random.normal(7.2, 0.05, 5), np.random.normal(25, 0.5, 5)]),'LSL': [7.0] * 5 + [20] * 5,'USL': [7.4] * 5 + [30] * 5})
    if batch_id == 'AVC-DM1-P3-B006':
        ipc_data.loc[6, 'Value'] = 29.8 
        ipc_data.loc[7, 'Value'] = 30.1 # OOS
    analytical_data = pd.DataFrame({'Test': ['Purity (HPLC)', 'Concentration (A280)', 'Endotoxin'],'Specification': ['> 98.0%', '20 ± 2.0 mg/mL', '< 0.5 EU/mL'],'Result': [f"{np.random.normal(99.1, 0.2):.1f}%", f"{np.random.normal(20.1, 0.3):.1f} mg/mL", f"< {np.random.uniform(0.1, 0.2):.2f} EU/mL"]})
    return ipc_data, analytical_data
def generate_quality_data():
    return pd.DataFrame({'Deviation ID': ['DEV-24-015', 'CAPA-23-008', 'CR-24-031'],'CDMO': ['Catalent Pharma', 'WuXi Biologics', 'Fujifilm Diosynth'],'Type': ['Deviation', 'CAPA', 'Change Request'],'Description': ['Temperature excursion during upstream process step.', 'Implement new training for analytical method transfer.', 'Update master batch record with new stirring parameters.'],'Status': ['Investigation', 'Effectiveness Check', 'Pending Approval'],'Owner': ['Manager', 'Tech Dev', 'QA']})
def generate_budget_data():
    return pd.DataFrame({'CDMO': ['Catalent Pharma', 'WuXi Biologics', 'Lonza Group', 'Fujifilm Diosynth'],'Program': ['DM1', 'DMD/FSHD', 'DM1', 'DMD'],'Budget Type': ['OpEx', 'OpEx', 'CapEx', 'OpEx'],'Annual Budget ($M)': [15.0, 25.0, 10.0, 12.0],'Actuals YTD ($M)': [10.2, 18.5, 3.1, 8.0]})
def generate_tech_transfer_data():
    df = pd.DataFrame({'Task ID': ['TT-1.1', 'TT-1.2', 'TT-2.1', 'TT-3.1', 'TT-3.2', 'TT-4.1', 'TT-5.1'],'Task': ['Define Scope & Assemble VPT', 'Approve Tech Transfer Plan', 'Transfer Process & Analytical Methods', 'Complete Facility Fit & Gap Analysis', 'Qualify Raw Materials', 'Execute Engineering Batch', 'Execute 3x PPQ Batches'],'Lead Team': ['Ops', 'QA', 'Tech Dev', 'Engineering', 'Supply Chain', 'CDMO/Ops', 'CDMO/Ops'],'Planned Duration (Days)': [10, 5, 45, 20, 30, 15, 60],'Actual Duration (Days)': [10, 6, 50, 22, np.nan, np.nan, np.nan],'Start Date': pd.to_datetime(['2024-04-01', '2024-04-11', '2024-04-16', '2024-06-01', '2024-06-01', '2024-07-01', '2024-07-16']),'Dependencies': [None, 'TT-1.1', 'TT-1.2', 'TT-2.1', 'TT-2.1', 'TT-3.1,TT-3.2', 'TT-4.1']})
    df['Finish Date'] = df['Start Date'] + pd.to_timedelta(df['Actual Duration (Days)'].fillna(df['Planned Duration (Days)']), unit='D')
    return df
def generate_governance_data():
    return pd.DataFrame({'Date': [date(2024, 5, 20), date(2024, 7, 15), date(2024, 9, 9)],'CDMO': ['WuXi Biologics', 'Lonza Group', 'Catalent Pharma'],'Meeting Type': ['Quarterly Business Review', 'Person-in-Plant', 'Audit Preparation'],'Key Topics': ['Review Q1 KPIs, discuss upcoming forecast.', 'Observe critical conjugation step, provide real-time support.', 'Review data integrity practices for batch records.'],'Action Items': [2, 0, 4]})
