

<h1>Attendance Analysis Dashboard (Streamlit App)</h1>

<p>This Streamlit application provides detailed daily and cumulative attendance analysis based on daily CSV reports (e.g., <code>DD-Mon-YYYY.csv</code> files) containing student attendance status.</p>

<hr>

<h2>Prerequisites and Setup</h2>
<ul>
    <li>Python 3.x</li>
    <li>Required libraries: <code>pandas</code>, <code>xlsxwriter</code>, <code>matplotlib</code>, <code>numpy</code>, <code>streamlit</code>.</li>
    <li>Run the app using: <code>streamlit run your_script_name.py</code></li>
    <li>Attendance CSV files must be in the same directory as the script.</li>
</ul>

<hr>

<h2>Supported Analysis Types</h2>

<p>The sidebar allows you to switch between three main analysis modes:</p>

<div class="feature">
    <h3>1. Daily Attendance Report 🗓️</h3>
    <p>Provides a comprehensive analysis for a <strong>single selected day</strong>.</p>
    <ul>
        <li><strong>Summary:</strong> Total, Present, and Absent counts.</li>
        <li><strong>Late Biometric Punches:</strong> Lists students who punched in after <code>20:45:00</code> (configurable in <code>LATE_PUNCH_TIME_STR</code>).</li>
        <li><strong>Students to Notify:</strong> A simple list of all students marked as 'Not Present'.</li>
        <li><strong>Per Room Analysis:</strong> Separate reports for Present and Absent students, grouped and sorted by <strong>Block, Floor, and Room No.</strong></li>
        <li><strong>Download:</strong> Exports all sub-reports into a single Excel file with multiple sheets.</li>
    </ul>
</div>

<div class="feature">
    <h3>2. Monthly Attendance Graph 📊</h3>
    <p>Generates a bar chart showing the <strong>daily Present vs. Absent count trend</strong> across all days in the selected month, providing a high-level visual overview.</p>
</div>

<div class="feature">
    <h3>3. Reduction Days Report ⭐ </h3>
    <p>Calculates the <strong>cumulative number of days a student was absent</strong> (renamed from 'Cumulative Absence' to <strong>'Reduction Days'</strong>) across <strong>all available attendance files</strong>.</p>
    <h4>New Features: Location Filtering</h4>
    <ul>
        <li>The report now supports <strong>multi-select filtering</strong> in the sidebar.</li>
        <li>Users can filter the results by one or more <strong>Block(s)</strong>, <strong>Floor(s)</strong>, and <strong>Room No(s)</strong>.</li>
        <li>The report only displays students with a Reduction Days count greater than zero.</li>
        <li>The final report is sorted by Block, custom Floor order, and Room No.</li>
    </ul>
</div>

<hr>

<h2>Key Code Constants</h2>

<p>The following constants are used for configuration:</p>
<ul>
    <li><code>LATE_PUNCH_TIME_STR = '20:45:00'</code>: Defines the time considered "late" for the 'Late Biometric Punches' report.</li>
    <li><code>FLOOR_ORDER = [...]</code>: A list defining the <strong>custom sort order</strong> for floors (e.g., 'FirstFloor' before 'SecondFloor').</li>
    <li><code>DATE_FORMATS = [...]</code>: Multiple formats are supported to robustly parse dates from CSV filenames (e.g., '20-Jul-2025.csv').</li>
</ul>



