# utils.py
import pandas as pd
import numpy as np
from datetime import date, timedelta

def generate_cdmo_data():
    """Generates a list of mock CDMO partners with enriched performance and BCP metrics."""
    data = {
        'CDMO Name': ['Catalent Pharma', 'WuXi Biologics', 'Lonza Group', 'Fujifilm Diosynth'],
        'Location': ['Bloomington, IN, USA', 'Dundalk, Ireland', 'Visp, Switzerland', 'Hillerød, Denmark'],
        'Status': ['Active', 'Active', 'Onboarding', 'Active'],
        'Expertise': ['Antibody Production', 'Oligonucleotide Synthesis', 'AOC Conjugation & Fill-Finish', 'Antibody Production'],
        'Avg. On-Time Delivery (%)': [98, 85, 99, 92],
        'Avg. Batch Success Rate (%)': [95, 100, 100, 98],
        'Quality Score (1-100)': [88, 95, 99, 92],
        'Avg. Yield (%)': [82, 88, 85, 84],
        'Batches YTD': [12, 25, 4, 15],
        'BCP Status': ['Approved', 'Under Review', 'Draft', 'Approved'],
        'BCP Last Reviewed': [date(2023, 12, 1), date(2024, 6, 5), None, date(2024, 1, 15)]
    }
    return pd.DataFrame(data)

def generate_master_schedule():
    """Generates a master production schedule with enriched technical details."""
    today = date.today()
    data = {
        'Batch ID': ['AVC-DM1-P3-B005', 'AVC-DM1-P3-B006', 'AVC-DMD-P2-B003', 'AVC-FSHD-P2-B002', 'AVC-DMD-P2-B004', 'AVC-DM1-P3-B007'],
        'Product': ['AOC-1001', 'AOC-1001', 'AOC-1021', 'AOC-1044', 'AOC-1021', 'AOC-1001'],
        'Program': ['DM1', 'DM1', 'DMD', 'FSHD', 'DMD', 'DM1'],
        'CDMO': ['WuXi Biologics', 'Catalent Pharma', 'Fujifilm Diosynth', 'WuXi Biologics', 'Lonza Group', 'Catalent Pharma'],
        'Status': ['In Production', 'At Risk', 'Awaiting Release', 'Shipped', 'Planned', 'Failed'],
        'Start Date': [today - timedelta(days=30), today - timedelta(days=20), today - timedelta(days=60), today - timedelta(days=90), today + timedelta(days=10), today - timedelta(days=45)],
        'End Date': [today + timedelta(days=60), today + timedelta(days=45), today - timedelta(days=10), today - timedelta(days=30), today + timedelta(days=90), today - timedelta(days=15)],
        'Planned Cycle Time (Days)': [90, 65, 50, 60, 80, 30],
        'Actual Cycle Time (Days)': [92, 68, 51, 60, np.nan, 30],
        'Yield (%)': [88.1, np.nan, 84.5, 90.2, np.nan, 45.0],
        'Deviation ID': [None, 'DEV-24-015', None, None, None, 'DEV-24-018']
    }
    return pd.DataFrame(data)

# --- START: FIX ---
# Added the missing generate_risk_register function
def generate_risk_register():
    """Generates an enhanced risk register."""
    data = {
        'Risk ID': ['RSK-SUP-01', 'RSK-TECH-01', 'RSK-COMP-01', 'RSK-GEO-01'],
        'CDMO': ['WuXi Biologics', 'Lonza Group', 'All', 'Catalent Pharma'],
        'Description': ['Single-source for critical raw material faces shipping delays.', 'New conjugation process shows yield variability at scale.', 'Upcoming EMA inspection may scrutinize data integrity of batch records.', 'Geopolitical tensions could impact shipping lanes from US facility.'],
        'Impact': [4, 4, 5, 3], # 1-5 Scale
        'Probability': [3, 4, 2, 2], # 1-5 Scale
        'Owner': ['Supply Chain', 'Tech Dev', 'Quality', 'Manager'],
        'Mitigation Strategy': ['Qualify second supplier (Project OpEx-003).', 'Perform DOE to optimize process parameters.', 'Conduct internal audit and data review ahead of inspection.', 'Increase safety stock at domestic warehouse.'],
        'Mitigation Status': ['In Progress', 'Planned', 'In Progress', 'Complete']
    }
    df = pd.DataFrame(data)
    df['Risk Score'] = df['Impact'] * df['Probability']
    return df.sort_values(by='Risk Score', ascending=False)
# --- END: FIX ---

def generate_spc_data(batch_id, parameter='Oligo Concentration'):
    """Generates detailed SPC data for a batch process step."""
    np.random.seed(hash(batch_id) % (2**32 - 1))
    n_points = 20
    mean = 10.0 if parameter == 'Oligo Concentration' else 7.2
    std_dev = 0.2 if parameter == 'Oligo Concentration' else 0.05
    lsl = 9.5 if parameter == 'Oligo Concentration' else 7.0
    usl = 10.5 if parameter == 'Oligo Concentration' else 7.4
    
    data = np.random.normal(mean, std_dev, n_points)
    
    if batch_id == 'AVC-DM1-P3-B006': # At Risk batch
        data[15:] -= np.linspace(0, 0.4, 5) # Introduce a downward trend
    if batch_id == 'AVC-DM1-P3-B007': # Failed batch
        data[10:] = np.random.normal(mean - 0.5, std_dev*1.5, 10) # Introduce a shift
        data[18] = lsl - 0.1 # OOS point

    df = pd.DataFrame({'Measurement': range(1, n_points + 1), 'Value': data})
    df['Mean'] = mean
    df['UCL'] = mean + 3 * std_dev
    df['LCL'] = mean - 3 * std_dev
    df['USL'] = usl
    df['LSL'] = lsl
    return df

def generate_quality_data():
    """Generates data for the quality and compliance dashboard."""
    data = {
        'Record ID': ['DEV-24-015', 'CAPA-23-008', 'CR-24-031', 'DEV-24-018'],
        'CDMO': ['Catalent Pharma', 'WuXi Biologics', 'Fujifilm Diosynth', 'Catalent Pharma'],
        'Type': ['Deviation', 'CAPA', 'Change Request', 'Deviation'],
        'Description': ['Temperature excursion during upstream process step.', 'Implement new training for analytical method transfer.', 'Update master batch record with new stirring parameters.', 'Contamination event led to batch failure.'],
        'Status': ['Investigation', 'Effectiveness Check', 'Pending Approval', 'Root Cause Analysis'],
        'Priority': ['High', 'Medium', 'Low', 'Critical'],
        'Days Open': [15, 92, 5, 2]
    }
    return pd.DataFrame(data)

def generate_budget_data():
    """Generates hierarchical budget data."""
    data = {
        'Category': ['External Manufacturing', 'External Manufacturing', 'External Manufacturing', 'External Manufacturing', 'Supporting Activities', 'Supporting Activities'],
        'Sub-Category': ['Drug Substance', 'Drug Substance', 'Drug Product', 'Drug Product', 'Logistics', 'Consulting'],
        'CDMO': ['Catalent Pharma', 'Fujifilm Diosynth', 'Lonza Group', 'WuXi Biologics', 'Global', 'Global'],
        'Program': ['DM1', 'DMD', 'DMD/FSHD', 'DM1', 'All', 'All'],
        'Annual Budget ($M)': [15.0, 12.0, 10.0, 25.0, 3.0, 2.0],
        'YTD Actuals ($M)': [10.2, 8.0, 3.1, 18.5, 1.5, 1.8],
        'YTD Forecast ($M)': [11.0, 7.5, 4.0, 19.0, 1.8, 2.0]
    }
    return pd.DataFrame(data)

def generate_tech_transfer_data():
    """Generates structured data for a tech transfer project with risk."""
    data = {
        'Task ID': ['TT-1.1', 'TT-1.2', 'TT-2.1', 'TT-3.1', 'TT-3.2', 'TT-4.1', 'TT-5.1'],
        'Task': ['Define Scope & Assemble VPT', 'Approve Tech Transfer Plan', 'Transfer Process & Analytical Methods', 'Complete Facility Fit & Gap Analysis', 'Qualify Raw Materials', 'Execute Engineering Batch', 'Execute 3x PPQ Batches'],
        'Lead Team': ['Ops', 'QA', 'Tech Dev', 'Engineering', 'Supply Chain', 'CDMO/Ops', 'CDMO/Ops'],
        'Planned Duration (Days)': [10, 5, 45, 20, 30, 15, 60],
        'Actual Duration (Days)': [10, 6, 50, 22, np.nan, np.nan, np.nan],
        'Start Date': pd.to_datetime(['2024-04-01', '2024-04-11', '2024-04-16', '2024-06-05', '2024-06-05', '2024-07-08', '2024-07-23']),
        'Risk Level': ['Low', 'Low', 'High', 'Medium', 'High', 'Medium', 'High']
    }
    df = pd.DataFrame(data)
    df['Finish Date'] = df['Start Date'] + pd.to_timedelta(df['Actual Duration (Days)'].fillna(df['Planned Duration (Days)']), unit='D')
    return df

def generate_governance_data():
    """Generates enriched data for governance meetings."""
    data = {
        'Date': [date(2024, 2, 20), date(2024, 4, 15), date(2024, 5, 20)],
        'CDMO': ['WuXi Biologics', 'Catalent Pharma', 'WuXi Biologics'],
        'Meeting Type': ['Quarterly Business Review', 'Technical Working Group', 'Quarterly Business Review'],
        'Key Topics': ['Review Q4 KPIs, discuss 2024 forecast.', 'Investigate yield drop in B004.', 'Review Q1 KPIs, address DEV-24-015.'],
        'Actions Generated': [5, 2, 3],
        'Actions Closed': [5, 1, 1]
    }
    return pd.DataFrame(data)
    
def generate_op_ex_data():
    """Generates a portfolio of continuous improvement projects."""
    data = {
        'Project ID': ['OpEx-001', 'OpEx-002', 'OpEx-003', 'OpEx-004'],
        'Title': ['Improve Conjugation Yield', 'Reduce Cycle Time for Antibody Prod.', 'Qualify 2nd Supplier for Oligo', 'Automate Deviation Trending'],
        'Lead': ['Tech Dev', 'Manager', 'Supply Chain', 'Quality'],
        'CDMO': ['Lonza Group', 'Catalent Pharma', 'WuXi Biologics', 'All'],
        'Status': ['In Progress', 'Complete', 'In Progress', 'Planned'],
        'Start Date': [date(2024, 6, 1), date(2024, 1, 15), date(2024, 5, 1), date(2024, 8, 1)],
        'Target Completion': [date(2024, 12, 1), date(2024, 4, 30), date(2025, 2, 1), date(2024, 11, 30)],
        'Financial Impact ($K/yr)': [500, 250, 1500, 50],
        'Technical Feasibility (1-5)': [3, 5, 4, 5],
        'Implementation Cost ($K)': [75, 20, 300, 40]
    }
    df = pd.DataFrame(data)
    df['ROI'] = df['Financial Impact ($K/yr)'] / df['Implementation Cost ($K)']
    return df
