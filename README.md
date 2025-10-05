<h1>Project Summary: Attendance Analysis Dashboard 📊</h1>

<hr>

<h2>Primary Objective</h2>
<p>The project is an Attendance Analysis Dashboard built using Streamlit to process and analyze daily student attendance records from CSV files, providing both detailed daily reports and a visual monthly summary.</p>

<hr>

<h2>Key Technologies Used</h2>
<ul>
<li><strong>Streamlit:</strong> For creating the interactive web application interface.</li>
<li><strong>Pandas:</strong> The core library for reading, manipulating, and analyzing the attendance data (DataFrames).</li>
<li><strong>Matplotlib & NumPy:</strong> Used to generate the monthly comparative bar graph of present versus absent students.</li>
<li><strong>Xlsxwriter:</strong> Employed within Pandas to create multi-sheet Excel reports for detailed daily analysis.</li>
</ul>

<hr>

<h2>Core Analysis Features</h2>
<p>The program performs detailed analysis and generates several report sheets:</p>
<ol>
<li><strong>Daily Summary:</strong> Provides overall statistics, including total students, counts for 'Present', and counts for 'Not Present'.</li>
<li><strong>Late Biometric Punches:</strong> Identifies and lists students whose 'Last Punch' time is later than 20:45:00, flagging them as late.</li>
<li><strong>Students to Notify:</strong> Creates a sorted list of all students marked as 'Not Present'.</li>
<li><strong>Per-Room Analysis:</strong> If block, floor, and room information is available, it generates summarized reports for:
<ul>
<li><strong>Present Students per Room:</strong> Counts and lists the names of present students, sorted by Block and Floor (following a specific floor order).</li>
<li><strong>Absent Students per Room:</strong> Counts and lists the names of absent students, also sorted by Block and Floor.</li>
</ul>
</li>
</ol>

<hr>

<h2>Application Workflow</h2>
<ul>
<li><strong>Daily Report Generation:</strong> The user inputs a file name (e.g., <code>01-Jun-2025</code>), the program reads the corresponding <code>.csv</code> file, runs the analysis, and provides a downloadable Excel file containing all the reports.</li>
<li><strong>Monthly Visualization:</strong> The application automatically scans the directory for all available <code>.csv</code> files and compiles them to display a monthly attendance trend graph.</li>
</ul>
streak

