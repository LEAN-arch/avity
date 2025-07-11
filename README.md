A sophisticated, multi-page Streamlit dashboard designed to serve as the ultimate technical and analytical aid for an Operations Manager, External Manufacturing Operations at a biopharmaceutical company like Avidity Biosciences.
This application provides a single source of truth for managing a global network of Contract Development & Manufacturing Organizations (CDMOs), ensuring supply continuity, financial oversight, and operational excellence for Avidity's innovative AOC therapeutic pipeline.
The Challenge
Managing a global external manufacturing network presents significant challenges:
Lack of Visibility: Data is often fragmented across multiple CDMOs, spreadsheets, and reports, making it difficult to get a real-time, holistic view of the entire supply chain.
Reactive Problem-Solving: Issues such as production delays, quality deviations, or yield variability are often discovered after the fact, leading to costly investigations and potential supply disruptions.
Complex Coordination: Aligning internal teams (Supply Chain, Quality, Tech Dev) with multiple external partners requires a robust, data-driven communication and governance framework.
Demonstrating Oversight: Proving robust oversight and control over external partners is a key requirement for regulatory compliance (e.g., FDA, EMA).
The Solution
The External Manufacturing Command Center is a centralized, interactive platform that transforms raw operational data into actionable intelligence. It empowers the Operations Manager to move from reactive firefighting to proactive, strategic management by:
Visualizing Performance: Providing sophisticated, commercial-grade visualizations of KPIs, schedules, and process data.
Enabling Deep Dives: Allowing for granular analysis of specific CDMOs, batches, or projects.
Prioritizing Action: Using data-driven dashboards to immediately highlight risks, deviations, and areas requiring managerial attention.
Facilitating Governance: Serving as the central data hub for leading Virtual Plant Team (VPT) meetings, Quarterly Business Reviews (QBRs), and reporting to leadership.
Key Features
The application is structured into a main dashboard and several specialized analytical modules accessible via the sidebar:
1. Portfolio Dashboard (app.py)
Technical KPIs: At-a-glance metrics for overall batch success rate, cycle time variance, and portfolio average yield.
CDMO Performance Quadrant: A sophisticated bubble chart that plots all CDMOs on an On-Time Delivery vs. Batch Success Rate matrix, with bubble size representing production volume and color representing average yield. Immediately identifies top performers and partners needing attention.
Master Production Schedule: A network-wide Gantt chart visualizing all production and release timelines, color-coded by batch status.
2. CDMO Drilldown (pages/A_CDMO_Drilldown.py)
A 360-degree technical view of any selected CDMO partner, organized into powerful tabs:
Operational Performance: Funnel charts and Statistical Process Control (SPC) charts for key metrics like cycle time.
Batch Deep Dive: Select any batch to view its SPC data, highlighting out-of-spec conditions, and see final analytical results.
Quality & Compliance: An interactive tracker for all open deviations, CAPAs, and change requests.
Continuity & Mitigation: Tracks the status of Business Continuity Plans (BCPs) and provides an editable register for managing risk mitigation strategies.
3. Financial Oversight (pages/B_Financial_Oversight.py)
Hierarchical Budget Sunburst: A multi-dimensional view of the annual budget, allowing the manager to drill down from total budget to budget type (OpEx/CapEx), CDMO, and specific program.
Budget vs. Actuals Table: A clear, conditionally formatted table tracking spend against budget for each partner.
4. Tech Transfer Hub (pages/C_Tech_Transfer_Hub.py)
Critical Path Gantt Chart: A true project management tool that visualizes task durations, dependencies, and schedule variance for complex tech transfer projects. Delayed tasks are automatically highlighted in red.
5. Governance & Oversight (pages/D_Governance_and_Oversight.py)
Engagement Cadence Heatmap: Visualizes the frequency and type of interactions with each CDMO over time, ensuring a regular governance rhythm is maintained.
Official Engagement Log: An auditable, editable log for all formal meetings (QBRs, audits, etc.), tracking key topics and action items.
6. Operational Excellence (pages/E_Operational_Excellence.py)
Initiative Prioritization Matrix: An Impact vs. Feasibility scatter plot that helps prioritize continuous improvement projects based on financial impact, technical feasibility, and implementation cost.
Detailed Project Tracker: A portfolio view of all OpEx initiatives, their status, and their return on investment (ROI).
Tech Stack
Framework: Streamlit
Data Manipulation: Pandas, NumPy
Plotting: Plotly
