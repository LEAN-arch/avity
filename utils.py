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
    """Generates a comprehensive master production schedule across ALL CDMOs."""
    today = date.today()
    data = {
        'Batch ID': ['AVC-DM1-WU-B005', 'AVC-DM1-CA-B006', 'AVC-DMD-FU-B003', 'AVC-FSHD-WU-B002', 'AVC-DMD-LO-B004', 'AVC-DM1-CA-B007'],
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

def generate_risk_register():
    """Generates an enhanced risk register for all CDMOs."""
    data = {
        'Risk ID': ['RSK-SUP-01', 'RSK-TECH-01', 'RSK-COMP-01', 'RSK-GEO-01', 'RSK-PERS-01'],
        'CDMO': ['WuXi Biologics', 'Lonza Group', 'All', 'Catalent Pharma', 'Fujifilm Diosynth'],
        'Description': ['Single-source for critical raw material faces shipping delays.', 'New conjugation process shows yield variability at scale.', 'Upcoming EMA inspection may scrutinize data integrity.', 'Geopolitical tensions could impact shipping lanes from US facility.', 'Key technical lead at CDMO has high turnover risk.'],
        'Impact': [4, 4, 5, 3, 4], 'Probability': [3, 4, 2, 2, 3], 'Owner': ['Supply Chain', 'Tech Dev', 'Quality', 'Manager', 'Manager'],
        'Mitigation Strategy': ['Qualify second supplier (Project OpEx-003).', 'Perform DOE to optimize process parameters.', 'Conduct internal audit and data review.', 'Increase safety stock at domestic warehouse.', 'Establish knowledge transfer plan and identify backup.'],
        'Mitigation Status': ['In Progress', 'Planned', 'In Progress', 'Complete', 'Planned']
    }
    df = pd.DataFrame(data)
    df['Risk Score'] = df['Impact'] * df['Probability']
    return df.sort_values(by='Risk Score', ascending=False)

def generate_spc_data(batch_id, parameter='Oligo Concentration'):
    """Generates unique, deterministic SPC data for any given batch ID."""
    np.random.seed(hash(batch_id) % (2**32 - 1))
    n_points = 20
    mean = 10.0 if parameter == 'Oligo Concentration' else 7.2
    std_dev = 0.2 if parameter == 'Oligo Concentration' else 0.05
    lsl = 9.5 if parameter == 'Oligo Concentration' else 7.0
    usl = 10.5 if parameter == 'Oligo Concentration' else 7.4
    data = np.random.normal(mean, std_dev, n_points)
    if 'CA-B006' in batch_id: data[15:] -= np.linspace(0, 0.4, 5)
    if 'CA-B007' in batch_id: data[10:] = np.random.normal(mean - 0.5, std_dev*1.5, 10); data[18] = lsl - 0.1
    df = pd.DataFrame({'Measurement': range(1, n_points + 1), 'Value': data})
    df['Mean'] = mean; df['UCL'] = mean + 3 * std_dev; df['LCL'] = mean - 3 * std_dev
    df['USL'] = usl; df['LSL'] = lsl
    return df

def generate_quality_data():
    """Generates quality records for all CDMOs."""
    data = {
        'Record ID': ['DEV-24-015', 'CAPA-23-008', 'CR-24-031', 'DEV-24-018', 'CAPA-24-001'],
        'CDMO': ['Catalent Pharma', 'WuXi Biologics', 'Fujifilm Diosynth', 'Catalent Pharma', 'Lonza Group'],
        'Type': ['Deviation', 'CAPA', 'Change Request', 'Deviation', 'CAPA'],
        'Description': ['Temperature excursion during upstream process step.', 'Implement new training for analytical method transfer.', 'Update master batch record with new stirring parameters.', 'Contamination event led to batch failure.', 'Address yield variability in conjugation process.'],
        'Status': ['Investigation', 'Effectiveness Check', 'Pending Approval', 'Root Cause Analysis', 'Planned'],
        'Priority': ['High', 'Medium', 'Low', 'Critical', 'High'],
        'Days Open': [15, 92, 5, 2, 0]
    }
    return pd.DataFrame(data)

def generate_cdmo_kpis(cdmo_name):
    """Generates unique historical KPI data for a specific CDMO."""
    np.random.seed(hash(cdmo_name) % (2**32 - 1))
    qtrs = pd.to_datetime(['2023-03-31', '2023-06-30', '2023-09-30', '2023-12-31', '2024-03-31'])
    base_otd = 90 + np.random.randint(-5, 5)
    base_dev = 0.8 + np.random.uniform(-0.5, 0.5)
    otd = np.random.normal(base_otd, 2, 5).clip(80, 100)
    devs = np.random.normal(base_dev, 0.2, 5).clip(0, 2)
    data = {'Quarter': qtrs, 'On-Time Delivery (%)': otd, 'Deviations per Batch': devs}
    return pd.DataFrame(data)

def generate_cpk_data(cdmo_name):
    """Generates unique Cpk data for a specific CDMO."""
    np.random.seed(hash(cdmo_name) % (2**32 - 1))
    base_cpk = np.random.uniform(0.9, 1.5)
    data = {
        'Parameter': ['Oligo Concentration', 'pH', 'Antibody Titer', 'Conjugation Efficiency'],
        'Cpk Value': [base_cpk, base_cpk + 0.3, base_cpk - 0.2, base_cpk - 0.1]
    }
    return pd.DataFrame(data)

def generate_budget_data():
    return pd.DataFrame({'Category': ['External Manufacturing', 'External Manufacturing', 'External Manufacturing', 'External Manufacturing', 'Supporting Activities', 'Supporting Activities'],'Sub-Category': ['Drug Substance', 'Drug Substance', 'Drug Product', 'Drug Product', 'Logistics', 'Consulting'],'CDMO': ['Catalent Pharma', 'Fujifilm Diosynth', 'Lonza Group', 'WuXi Biologics', 'Global', 'Global'],'Program': ['DM1', 'DMD', 'DMD/FSHD', 'DM1', 'All', 'All'],'Annual Budget ($M)': [15.0, 12.0, 10.0, 25.0, 3.0, 2.0],'YTD Actuals ($M)': [10.2, 8.0, 3.1, 18.5, 1.5, 1.8],'YTD Forecast ($M)': [11.0, 7.5, 4.0, 19.0, 1.8, 2.0]})
def generate_tech_transfer_data():
    data = {'Task ID': ['TT-1.1', 'TT-1.2', 'TT-2.1', 'TT-3.1', 'TT-3.2', 'TT-4.1', 'TT-5.1'],'Task': ['Define Scope & Assemble VPT', 'Approve Tech Transfer Plan', 'Transfer Process & Analytical Methods', 'Complete Facility Fit & Gap Analysis', 'Qualify Raw Materials', 'Execute Engineering Batch', 'Execute 3x PPQ Batches'],'Lead Team': ['Ops', 'QA', 'Tech Dev', 'Engineering', 'Supply Chain', 'CDMO/Ops', 'CDMO/Ops'],'Planned Duration (Days)': [10, 5, 45, 20, 30, 15, 60],'Actual Duration (Days)': [10, 6, 50, 22, np.nan, np.nan, np.nan],'Start Date': pd.to_datetime(['2024-04-01', '2024-04-11', '2024-04-16', '2024-06-05', '2024-06-05', '2024-07-08', '2024-07-23']),'Risk Level': ['Low', 'Low', 'High', 'Medium', 'High', 'Medium', 'High'],'Progress (%)': [100, 100, 100, 100, 75, 20, 0]}
    df = pd.DataFrame(data); df['Finish Date'] = df['Start Date'] + pd.to_timedelta(df['Planned Duration (Days)'], unit='D')
    return df
def generate_governance_data():
    return pd.DataFrame({'Date': [date(2024, 2, 20), date(2024, 4, 15), date(2024, 5, 20)],'CDMO': ['WuXi Biologics', 'Catalent Pharma', 'WuXi Biologics'],'Meeting Type': ['Quarterly Business Review', 'Technical Working Group', 'Quarterly Business Review'],'Key Topics': ['Review Q4 KPIs, discuss 2024 forecast.', 'Investigate yield drop in B004.', 'Review Q1 KPIs, address DEV-24-015.'],'Actions Generated': [5, 2, 3],'Actions Closed': [5, 1, 1]})
def generate_op_ex_data():
    data = {'Project ID': ['OpEx-001', 'OpEx-002', 'OpEx-003', 'OpEx-004'],'Title': ['Improve Conjugation Yield', 'Reduce Cycle Time for Antibody Prod.', 'Qualify 2nd Supplier for Oligo', 'Automate Deviation Trending'],'Lead': ['Tech Dev', 'Manager', 'Supply Chain', 'Quality'],'CDMO': ['Lonza Group', 'Catalent Pharma', 'WuXi Biologics', 'All'],'Status': ['In Progress', 'Complete', 'In Progress', 'Planned'],'Start Date': [date(2024, 6, 1), date(2024, 1, 15), date(2024, 5, 1), date(2024, 8, 1)],'Target Completion': [date(2024, 12, 1), date(2024, 4, 30), date(2025, 2, 1), date(2024, 11, 30)],'Financial Impact ($K/yr)': [500, 250, 1500, 50],'Technical Feasibility (1-5)': [3, 5, 4, 5],'Implementation Cost ($K)': [75, 20, 300, 40]}
    df = pd.DataFrame(data); df['ROI'] = df['Financial Impact ($K/yr)'] / df['Implementation Cost ($K)']
    return df
